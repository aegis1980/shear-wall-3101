from typing import List
import math 
from enum import Enum
from platform import mac_ver


DEFAULTS ={
    'sci_v' : 0.75
}

class AnalysisType(Enum):
    ELASTIC=0,
    LIMITED_DUCTILE=1,
    FULLY_DUCTILE =2,

BAR_SIZES = [6, 8, 10, 12, 16, 20 ,36, 40]
WALLTYPES  = ['Elastic', 'Limited ductile', 'Fully ductile']

class ShearWall:

    def __init__(
            self,
           t : int, 
           l_w : int,
           f_c : int,
           f_y : int,
           d_bl : int, 
           s_v : int,
           n_l:int,
           c_end: int, 
           axial_load: float = 0,
           f_yt : int = None,
        ):
            self.l_w = l_w
            self.t = t
            self.f_c  =f_c
            self.f_y = f_y
            self.f_yt = f_yt or f_y
            self.d_bl = d_bl
            self.s_v = s_v
            self.n_l :int= n_l
            self.c_end : int = c_end 
            self.Nu  = axial_load



    def update(self):
        self.bar_x : List[int] = [] # bars positions. x=0 is end of wall

        self.warnings : List[str] = [] # warnings mean something has been changed to meet requirements. 
        self.logs : List[str] = [] 
        self.errors : List[str] = [] # errors terminate solver

        self.check_d_bl()
        self.check_sv_max()
        self.calc_barpositions()
        self.calc_a_s()
        self.calc_rho_n()
        self.check_rho_nmin()


    def check_d_bl(self) -> int:
        """
        bar diameter check

        """
        max_d: int = int(self.t/10)
        if self.type == AnalysisType.ELASTIC:
            max_d  = int(self.t/7)
            msg = "For elastic analysis, bar dia limited to (wall thickness / 7)"
        elif self.type == AnalysisType.LIMITED_DUCTILE:
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
            self.logs.append('Bar diameter okay')
            self.logs.append(msg)
            return True
            


    def check_sv_max(self):
        if self.t * 3 > 450:
            self.t = 450
            self.warnings.append("Vertical spacing limited to lesser of (3 x wall thickness) & 450mm")

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
        self.a_s =  self.n_l*(self.d_bl**2)*math.pi*self.lw / ( 4*self.s_v)
        return self.a_s


    def calc_barpositions(self):
        """ calculates bar positions

        """
        l_avail = self.l_w - (2*(self.c_end + self.d_v)+ self.d_bl)
        n_bars = math.ceiling(l_avail / self.s_v)
        l_occ = self.s_v * n_bars
        x_0 = (self.l_w - l_occ)/ 2 # centre the n bar in available space. this is first bar position.
        
        for i in range(n_bars):
            x = x_0 + self.s_v * i
            self.bar_x.append(x)
        







    def calc_rho_n(self):
        """
        Reo ratio

        Returns:
            [type]: [description]
        """
        self.rho_n = self.a_s/(self.t*self.l_w)
        return self.rho_n


    def check_rho_nmin(self):
        r1 = math.sqrt(self.f_c/(4*self.f_y))
        r2 = 0.7/self.f_y
        r3 = 0.0014
        rho_min = max(r1,r2,r3)

        if (self.rho_n <=0):
            self.error.append('Something wrong with checking min vertical reo ratio')
            return False
        elif self.rho_n < rho_min:
            self.error.append('Vertical reo area < min allowable')
            return False
        self.logs.append('Vertical reo ratio > min allowed. ok.')
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
            self.b1 = 0.85 - 0.004*(self.f_c-30)
        else: 
            self.b1 =0.65
        
        return self.a1,self.b1


    def solve_neutral_axis(self) -> int:
        a1, b1 = self.calc_a1_b1()
        n_bars = len(self.bar_x)

        tension = [True] * n_bars
        e_s = [0] * n_bars
        f_s = [0] * n_bars
        F_s = [0] * n_bars
        M_s = [0] * n_bars

        c = self.l_w / 2

        for i in range(n_bars):
            tension[i] = self.bar_x[i] > c
            if tension[i]:
                e_s[i] = 0.003*(self.bar_x[i]-c)/ c
            else:
                e_s[i] = 0
                

            f_s[i] = max(e_s[i] * 200000,self.f_y) # NOTE Shouldnt this be factored Mpa 
            F_s[i] = f_s[i] * (self.d_bl**2) * math.pi * self.n_l /4000 #kN
            M_s[i] = F_s[i] * (self.bar_x[i]-0.5 * b1 * c)/1000

        Ts = sum(F_s) # kN
        Cc = c * a1 * b1 * self.f_c * self.t /1000 #kN shooulnt f_c be factored?      

        Ms = sum(M_s)































































        
