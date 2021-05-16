from pathlib import Path
import base64
from shearwall import ShearWall,AnalysisType, BAR_SIZES, interaction_curve
import streamlit as st
import plotly.graph_objects as go

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

st.sidebar.markdown("Experimental webapp for design of shear wall to NZS3101.")
st.sidebar.markdown("Everything here is entirely untested, so not to be for anything other than play! 😵")
st.sidebar.markdown("Code is [here](https://github.com/aegis1980/shear-wall-3101). If you find an error or add a feature, **please** make a pull request.")     
st.sidebar.markdown('''
<small>See [readme](https://github.com/aegis1980/shear-wall-3101/blob/main/README.md), and [license](https://github.com/aegis1980/shear-wall-3101/blob/main/LICENSE).</small>
''', unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("[1. Analysis type](#analysis-type)")
st.sidebar.markdown("[2. Design actions](#design-actions)")
st.sidebar.markdown("[3. Wall dimensions](#wall-dimensions)")
st.sidebar.markdown("[4. Concrete props](#concrete)")
st.sidebar.markdown("[5. Reo props](#reo)")
st.sidebar.markdown("---")
st.sidebar.markdown("[Results](#results)")

at_column, left_column = st.beta_columns([1,3])
with at_column:
    st.subheader('Analysis type')
with left_column:
    atype=st.selectbox(label ='Select analysis type', options = ['Elastic', 'Limited ductile', 'Fully ductile'])


da_column,n_column, m_column, v_column = st.beta_columns(4)

with da_column:
    st.subheader('Design actions') 
with n_column:
    axial = st.text_input(label='ULS Axial load (kN)',value =2500)
    axial = str_to_int(axial)
with m_column:    
    moment = st.number_input(label='ULS Moment (kNm)',value =21000)
with v_column:  
    shear = st.number_input(label='ULS Shear (kN)',value =220)


wd_column,t_column, l_column , blank1= st.beta_columns(4)
with wd_column:
    st.subheader('Wall dims')
with t_column:
    t = st.number_input(label='Enter wall thickness (mm)',value =200)
with l_column:
    l_w = st.number_input(label='Enter wall length (mm)', value = 3000)
    

sp_column,fc_column, c_column , blank2= st.beta_columns(4)

with sp_column:
    st.subheader('Concrete')
with fc_column:
    f_c = st.number_input(label='Compression strength (MPa)', value = 40)
with c_column:
    c_end = st.number_input(label='Cover to steel (mm)', value = 40)


reo_column, v_column, h_column, s_column = st.beta_columns(4)
with reo_column:
    st.subheader('Reo')
with v_column:
    st.subheader('Vertical steel')
    d_bl = st.selectbox(label= 'Dia vertical steel (mm)', options = BAR_SIZES)
    f_y = st.number_input(label='Vert reo yield strength (MPa)', value = 500)
    s_v = st.number_input(label='Spacing of vertical bars (mm)', value = 300)
    n_l = st.number_input(label='Number of layers steel', value =2, help="e.g. If single layer of vertical reo in front of wall and single layer in back, then n=2")
with h_column:
    st.subheader('Horizontal steel')
    d_bh = st.selectbox(label= 'Dia horizontal steel (mm)', options = BAR_SIZES)
    f_yt = st.number_input(label='Horiz reo yield strength (MPa)', value = 500)
with s_column:
    st.subheader('Stirrups')
    d_s = st.selectbox(label= 'Dia stirrups (mm)', options = BAR_SIZES)
    f_ys = st.number_input(label='Stirrups yield strength (MPa)', value = 500)


m,n = interaction_curve(
    atype=atype,
    t = t, 
    l_w = l_w,
    f_c=f_c,
    f_y=f_y,
    f_yt=f_yt,
    d_bl=d_bl,
    d_s=d_s,
    s_v=s_v,
    n_l=n_l,
    c_end=c_end
)


fig = go.Figure()

fig.add_trace(go.Scatter(x =m,y=n,mode= 'lines' ))
fig.add_trace(go.Scatter(x = [moment], y = [axial], mode='markers'))        

fig.update_layout(
    xaxis_title="Moment/ kNm",
    yaxis_title="Axial/ kN",
    showlegend=False
)

st.header ('Results')

gph_column, res_column = st.beta_columns(2)
with gph_column:    
    st.subheader('Interaction curve')
    st.plotly_chart(fig, use_container_width= True)





