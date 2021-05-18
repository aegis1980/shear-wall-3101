
from typing import List, Tuple
import math 
from enum import Enum

from scipy.optimize import fsolve

"""cl2.3.2.2 Strength reduction factors """
PHI_V = 0.75
PHI = 0.85 # general
PHI_SINGLE = 0.7 # single-reinforced.


ELASTIC=0
LIMITED_DUCTILE=1
FULLY_DUCTILE =2

BAR_SIZES = [10, 12, 16, 20 ,36, 40] # min bar size 10mm cl 11.3.12.2(b)
WALLTYPES  = ['Elastic', 'Limited ductile', 'Ductile']

class ShearWall:

    def __init__(
            self,
           t : int, 
           l_w : int,
           f_c : int,
           f_y : int,
           d_bl : int, 
           d_s: int,
           s_v : int,
           n_l:int,
           c_end: int, 
           N_u: float,
           atype: int,
           h_n: int = None,
           h_w: int = None,
           N_o: float = None,
           f_yt : int = None,
           f_ys : int = None,
    
        ):
            self.l_w = l_w
            self.t = t
            self.f_c  =f_c
            self.f_y = f_y
            self.f_yt = f_yt or f_y
            self.f_ys = f_ys or f_y
            self.d_bl = d_bl # dia of vertical bars
            self.d_s = d_s # dia of stirrups
            self.s_v = s_v
            self.n_l :int= n_l
            self.c_end : int = c_end 
            self.h_w : int = h_w  # total height of wall
            self.h_n : int = h_n or h_w # clear vertical height of wall

            self.N_u  = N_u # Design ULS axial load
            self.N_o = N_o # Design axial load (overstrength)
            self.atype = atype # analysis type

            self._auto_update: bool = False


    def update(self):
        self.bar_x : List[int] = [] # bars positions. x=0 is end of wall

        self.warnings : List[str] = [] # warnings mean something has been changed to meet requirements. 
        self.logs : List[str] = [] 
        self.errors : List[str] = [] # TODO errors terminate solver

        self.check_d_bl()
        self.check_sv_max()
        self.calc_barpositions()
        self.calc_a_s()
        self.calc_p_l()
        self.check_rho_nmin()
        self.check_rho_nmax()
        self.check_axial_uls()
        self.check_axial_overstrength()
        self.check_min_thickness()


    def check_d_bl(self) -> int:
        """
        bar diameter check

        """
        if self.d_bl <10:
            self.d_bl = 10
            self.warnings.append(f'cl11.3.12.2(b) Longitudinal bars cannot be < 10mm in diameter. Diameter increased to 10mm')

        max_d: int = int(self.t/10)
        if self.atype == ELASTIC:
            max_d  = int(self.t/7)
            msg = "For elastic analysis, bar dia limited to (wall thickness / 7)"
        elif self.atype == LIMITED_DUCTILE:
            max_d = int(self.t/8)
            msg = "For limited ductile analysis, bar dia limited to (wall thickness / 8)"
        else: 
            max_d = int(self.t/10)
            msg = "For fully ductile analysis bar dia limited to (wall thickness / 10)"

        if self.d_bl > max_d:
            self.warnings.append('Max bar > limit')
            self.warnings.append(msg)
            self.d_bl = max_d
            return False
        else:
            self.logs.append(f'Bar diameter okay, unchanged from {self.d_bl}')
            self.logs.append(msg)
            return True
            


    def check_sv_max(self):
        """
        11.3.12.2 Refer placement of reo in walls

        Returns:
            [type]: [description]
        """
        s1 = 3 * self.t
        s2 = 300
        smax= max(s1,s2)
        if self.s_v > smax :
            self.s_v = smax
            self.warnings.append("cl11.3.12.2(c) Vertical spacing limited to lesser of (3 x wall thickness) & 300mm")
            self.warnings.append(f'Spacing reduced to {smax}')
            return False
        return True

    def calc_a_s(self):
        """
        Wall reo area

        Args:
            lw (int): length of wall
            d_bl (int): long'l bar dia
            s_v (int): spacing of vert reo
            n_l (int): layers of long'l reo
        
        NOTE spreadsheet does not stipulated n_l bing long'l 

        Returns:
            area : calculated long'l wall reo 
        """
        self.a_s =  self.n_l*(self.d_bl**2)*math.pi*self.l_w / ( 4*self.s_v)
        self.logs.append(f'Area long steel, As= {self.a_s}')
        return self.a_s


    def calc_barpositions(self):
        """ calculates bar positions

        """
        l_avail = self.l_w - (2*(self.c_end + self.d_s)+ self.d_bl)
        n_bars = math.floor(l_avail / self.s_v) +1
        l_occ = self.s_v * (n_bars-1)
        x_0 = (self.l_w - l_occ)/ 2 # centre the n bar in available space. this is first bar position.
        
        for i in range(n_bars):
            x = x_0 + self.s_v * i
            self.bar_x.append(x)
        

    def calc_p_l(self):
        """
        Reo ratio

        Returns:
            [type]: [description]
        """
        self.p_l = self.a_s/(self.t*self.l_w)
        self.logs.append(f'Vertical reo ratio {self.p_l}')
        return self.p_l


    def check_rho_nmin(self) -> bool:
        """
        Refer cl 11.2.12.3 Minimum (and maximum) area of reinforcement.

        Returns:
            bool: True if a pass. False if not.
        """

        r1 = math.sqrt(self.f_c/(4*self.f_y)) #ref 11.3.12.3
        r2 = 0.7/self.f_y #TODO does this still apply
        r3 = 0.0014 #TODO ditto
        rho_min = max(r1,r2,r3)

        if (self.p_l <=0):
            self.error.append('Something wrong with checking min vertical reo ratio')
            return False
        elif self.p_l < rho_min:
            self.errors.append('cl11.3.12.3(c) Vertical reo area < min allowable')
            return False
        self.logs.append('cl11.3.12.3(c) Vertical reo ratio > min allowed. ok.')
        return True


    def check_rho_nmax(self):
        """
        Refer cl 11.2.12.3 Minimum (and maximum) area of reinforcement.

        Returns:
            bool: True if a pass. False if not.
        """

        r1 = 16/self.f_y

        if self.p_l > r1:
            self.error.append('cl11.3.12.3(b) Vertical reo area > max allowable')
            return False
        return True


    def check_axial_uls(self) -> bool:
        phi = PHI if self.n_l > 1 else PHI_SINGLE
        self.N_umax = 0.3 * phi * self.f_c * self.l_w * self.t /1000 #kN
        if self.N_umax < self.N_u:
            self.errors.append(f'cl11.3.1.6 ULS axial design load exceeds permissible limit, ${int(self.N_umax)}kN$')   
            return False
        return True



    def check_axial_overstrength(self) -> bool:
        """
        Applies only to limited ductile and ductile wall
        and appled to design axial load from overstrength
        Refer to cl 11.4.1.1
        TODO implement o/s in front-end

        Returns:
            bool: True if a pass (or elastic). False if fails check.
        """
        if self.atype ==ELASTIC:
            return True

        if not self.N_o:
            self.warnings.append('cl11.4.1.1 Max axial action of ductile wall could not be checked as $N_O^*$ not set')
            return True

        if self.N_o > 0.3 * self.t * self.l_w:
            self.errors.append("cl11.4.1.1 Design overstrength axial load exceeds limit,  $N_O^* > 0.3 A_g f'_c$")
            return False
        return True

    def check_min_thickness(self) -> bool:
        """
        To safegarud against buckling prior to plastic region developing.
        Only applies to limited ductile and ductile wall.

        Returns: 
            bool: True if a pass (or elastic). False if fails check.
        """
        if self.atype==ELASTIC:
            return True

        a=1
        b = 5 if self.atype== LIMITED_DUCTILE else 7
        k_m =  min(1,self.h_n / (0.25 + 0.055*self.h_w/self.l_w)*self.l_w) if self.h_n else 1 
        ep = max(1,0.3 -  (self.p_l*self.f_y)/(2.5*self.f_c))
        t_min = (a * k_m * b * (self.h_w/self.l_w + 2)* self.l_w) / (1700 * math.sqrt(ep))

        if self.t < t_min:
            self.errors.append(f'cl11.4.3.2 Wall less than $t_m = {int(t_min)}mm$')
            return False
        return True


    def calc_a1_b1(self):
        if self.f_c <=55:
            self.a1 = 0.85
        elif self.f_c <= 80:
            self.a1 = 0.85 - 0.004*(self.f_c-55)
        else: 
            self.a1 = 0.75

        if self.f_c < 30:
            self.b1 = 0.85
        elif self.f_c < 55:
            self.b1 = 0.85 - 0.008*(self.f_c-30)
        else: 
            self.b1 =0.65
        self.logs.append(f'alpha1 = {self.a1}')
        self.logs.append(f'beta1 = {self.b1}')
        return self.a1,self.b1


    def solve(self,limit: float =0.1, x0 : float =None) -> int:
        a1, b1 = self.calc_a1_b1()
        n_bars = len(self.bar_x)
        self.logs.append(f'Number of bars {n_bars}')

        tension = [True] * n_bars
        e_s = [0] * n_bars
        f_s = [0] * n_bars
        F_s = [0] * n_bars
        M_s = [0] * n_bars

        Cc =0

        def solve_fn(x : float, report = False):
            """
            Calculate total axis force for given n.a. position.

            Args:
                x (float): (assumed) n.a. position
                report (bool, optional): Defaults to False, for optimisation. Set to True to gt solution meta-data (with x = x_solution)

            Returns:
                float: net forces in wall section
            """
            for i in range(n_bars):
                tension[i] = self.bar_x[i] > x
               
                if tension[i]:
                    e_s[i] = 0.003*(self.bar_x[i]-x)/ x
                else:
                    e_s[i] = 0
                    

                f_s[i] = min(e_s[i] * 200000,self.f_y) # NOTE Shouldnt this be factored Mpa 
                F_s[i] = f_s[i] * (self.d_bl**2) * math.pi * self.n_l /4000 #kN
                M_s[i] = F_s[i] * (self.bar_x[i]-0.5 * b1 * x)/1000

            Ts = sum(F_s) # kN
            Cc = x * a1 * b1 * self.f_c * self.t /1000 #kN shooulnt f_c be factored?      
            Ms = sum(M_s)
            
            if not report:
                return (Ts+ self.N_u) - Cc # for force equilbirum
            else:
                return tension, e_s, f_s, F_s, M_s, Ts, Cc, Ms
        

        x0 = x0 or self.l_w/2
        x_na = fsolve(solve_fn,[x0])[0]

        tension, e_s, f_s, F_s, M_s, Ts, Cc, Ms = solve_fn(x_na,True)

        Mn = self.N_u*(0.5*self.l_w - (0.5 * b1* x_na))/1000

        self.th_Mn= 0.85 *(Ms + Mn)
        
        return x_na,self.th_Mn

    def shear(self):
        v_n = 1000 * self.Vu /(0.75 * 0.8 * self.t * self.l_w)
        v_max = min(0.2 * self.f_c,8)
        Vc = 0


# - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] - - [] -

def interaction_curve(
    t : int, 
    l_w : int,
    f_c : int,
    f_y : int,
    d_bl : int, 
    d_s: int,
    s_v : int,
    n_l:int,
    c_end: int, 
    atype: int,
    h_w : int, 
    f_yt : int = None
) -> Tuple[List[float],List[float]]:

    N_ok = []
    M_ok = []
    N_notok = []
    M_notok = []
    m=0
    last_m = 0
    n=0
    count = 0
    count_limit = 100 
    last_x_na : float = None # use this to seed the next solve - should be quicker?
    while True:        
        sw = ShearWall(
            atype=atype,
            t = t, 
            l_w = l_w,
            f_c=f_c,
            f_y=f_y,
            d_bl=d_bl,
            d_s=8,
            s_v=s_v,
            n_l=n_l,
            c_end=c_end,
            N_u=n,
            h_w=h_w
            
        )
        sw.update()
       
        last_x_na, m = sw.solve(limit = 0.5, x0 = last_x_na)
            
        last_m = m
        # a bit crappy: upper limit on N_ULS
        if sw.N_umax < n:
            N_ok.append(sw.N_umax)
            N_notok.append(n)
            M_notok.append(m)
        else:
            N_ok.append(n)

        M_ok.append(m)
        n +=sw.N_umax/20 # TODO be a bit smarter with this increment. 
        count +=1
        if count>count_limit or m<0:
            break


    return M_ok,N_ok, M_notok, N_notok



























































