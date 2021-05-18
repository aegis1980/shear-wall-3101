from pathlib import Path
import base64

import streamlit as st
import plotly.graph_objects as go

from shearwall import ShearWall, BAR_SIZES, interaction_curve
import tooltips

A_TYPES = ['Elastic', 'Limited ductile', 'Fully ductile']

def str_to_int(in_str : str):
    try:
        return int(in_str)
    except ValueError:
        st
        st.error("Please input number")
        #st.stop()
        return 0


# Thanks to streamlitopedia for the following code snippet

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded



# Initial page config
st.set_page_config(
     page_title='Techos.io | Shear wall to NZS3101 (Experimental!)',
     layout="wide",
     initial_sidebar_state="expanded",   
)


st.sidebar.markdown("Experimental web-app for design of shear wall to NZS3101:2016 (Amendment 3). **WIP**")
st.sidebar.markdown("Everything here is entirely untested, so not to be for anything other than play! 😵")
st.sidebar.markdown("Code is [here](https://github.com/aegis1980/shear-wall-3101). If you find an error or add a feature, **please** make a pull request.")     
st.sidebar.markdown('''
<small>See [readme](https://github.com/aegis1980/shear-wall-3101/blob/main/README.md), and [license](https://github.com/aegis1980/shear-wall-3101/blob/main/LICENSE).</small>
''', unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("[1. Analysis type](#analysis-type)")
st.sidebar.markdown("[2. Design actions](#design-actions)")
st.sidebar.markdown("[3. Wall dimensions](#dims)")
st.sidebar.markdown("[4. Concrete properties](#concrete)")
st.sidebar.markdown("[5. Reinforcement properties](#reo)")
st.sidebar.markdown("[Results](#results)")
st.sidebar.markdown("---")

c1,c2 = st.sidebar.beta_columns([2,1])
with c2:    
    st.image('./techos_logo_white.svg', width=50)
with c1:
    # st.markdown('''
    # <small>[techos.io]()</small>
    # ''', unsafe_allow_html=True)
    st.markdown('''
    <small>(c)2021 Jon Robinson</small>
    ''', unsafe_allow_html=True)
    st.markdown('''
    <small>MIT license.</small>
    ''', unsafe_allow_html=True)

st.subheader('Analysis type')
atype_str : str=st.selectbox(label ='Select analysis type', options = A_TYPES)

st.subheader('Design actions')
n_column, m_column, v_column = st.beta_columns(3)
 
with n_column:
    axial = st.text_input(label='ULS Axial load (kN)',value =3000)
    axial = str_to_int(axial)
with m_column:    
    moment = st.number_input(label='ULS Moment (kNm)',value =2100)
with v_column:  
    shear = st.number_input(label='ULS Shear (kN)',value =300)

st.subheader('Wall dimensions', anchor = 'dims')
t_column, l_column , hw_column= st.beta_columns(3)  
with t_column:
    t = st.number_input(label='Enter wall thickness (mm)',value =200)
with l_column:
    l_w = st.number_input(label='Enter wall length (mm)', value = 3000)
with hw_column:
    h_w = st.number_input(label='Enter wall height (mm)', value = 2800, help = tooltips.WALL_HEIGHT)    

st.subheader('Concrete properties', anchor = 'concrete')
fc_column, c_column , blank2= st.beta_columns(3)
with fc_column:
    f_c = st.number_input(label='Compression strength (MPa)', value = 40)
with c_column:
    c_end = st.number_input(label='Cover to steel (mm)', value = 40)

st.subheader('Reinforcement properties', anchor = 'reo')
v_column, h_column, s_column = st.beta_columns(3)
with v_column:
    st.markdown('**Vertical steel**')
    d_bl = st.selectbox(label= 'Dia vertical steel (mm)', options = BAR_SIZES,index = 4)
    f_y = st.number_input(label='Vert reo yield strength (MPa)', value = 500)
    s_v = st.number_input(label='Spacing of vertical bars (mm)', value = 300)
    n_l = st.number_input(label='Number of layers steel', value =2, help="e.g. If single layer of vertical reo in front of wall and single layer in back, then **n=2**")
with h_column:
    st.markdown('**Horizontal steel**')
    d_bh = st.selectbox(label= 'Dia horizontal steel (mm)', options = BAR_SIZES, index = 2)
    f_yt = st.number_input(label='Horiz reo yield strength (MPa)', value = 500)
    s_h = st.number_input(label='Spacing of horizontal bars (mm)', value = 300)
   
with s_column:
    st.markdown('**Stirrups**')
    d_s = st.selectbox(label= 'Dia stirrups (mm)', options = BAR_SIZES)
    f_ys = st.number_input(label='Stirrups yield strength (MPa)', value = 500)


st.header ('Results')
gph_column, res_column = st.beta_columns(2)

with gph_column:    
    st.subheader('Interaction curve')
    show_all_curve = st.checkbox(label = 'Include curve where axial load limit exceed', value = False, help = tooltips.FULL_CURVE)

m,n,m_notok, n_notok = interaction_curve(
    atype=A_TYPES.index(atype_str),
    t = t, 
    l_w = l_w,
    f_c=f_c,
    f_y=f_y,
    f_yt=f_yt,
    d_bl=d_bl,
    d_s=d_s,
    s_v=s_v,
    n_l=n_l,
    c_end=c_end,
    h_w = h_w
)


fig = go.Figure()

fig.add_trace(go.Scatter(name="Interaction boundary", x =m,y=n,mode= 'lines' , line=go.scatter.Line(color="blue", width=2)))
if show_all_curve:
    fig.add_trace(go.Scatter(name = "Limit exceeded", x=m_notok, y= n_notok, line=go.scatter.Line(color="blue",width=1,dash="dot" )))
fig.add_trace(go.Scatter(
        x = [moment], 
        y = [axial], 
        mode='markers', 
        marker = go.scatter.Marker(size=12,color = "red", line =dict(width=2,
                                            color='DarkSlateGrey')),
        hovertemplate =
        '<b>Nu</b>: %{y}kN'+
        '<br><b>Mu</b>: %{x}kNm'                               
     ))        

fig.update_layout(
    xaxis_title="Moment/ kNm",
    yaxis_title="Axial/ kN",
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20),
)


fig.update_xaxes(
    showgrid=False,
    fixedrange=True,
    rangemode="nonnegative",
    range = [0,max(m)*1.1]
)

fig.update_yaxes(
    showgrid=False,
    fixedrange=True,
    rangemode="nonnegative",
)

with gph_column:    
    st.plotly_chart(fig, use_container_width= True)





