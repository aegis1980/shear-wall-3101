from shearwall import ShearWall,AnalysisType, BAR_SIZES, interaction_curve
import streamlit as st
import plotly.graph_objects as go

st.sidebar.markdown(
    "Experimental webapp for design of shear wall to NZS3101." \
    "Everything here is entirely untested, so this must not be used for engineering design or verification." 
)
st.sidebar.markdown(
    "Code is here." \
    "Two requests:" \
    " If you find an error or add a feature, please "
    " Respect the license"     
)
st.sidebar.subheader("")
st.sidebar.markdown("[Analysis type](#analysis-type)")
st.sidebar.markdown("[Design actions](#design-actions)")
st.sidebar.markdown("[Wall dimensions](#wall-dimensions)")
st.sidebar.markdown("[Concrete props](#concrete)")


st.header('Analysis type')
atype=st.selectbox(label ='', options = ['Elastic', 'Limited ductile', 'Fully ductile'])

st.header('Design actions')
n_column, m_column, v_column = st.beta_columns(3)
with n_column:
    axial = st.number_input(label='ULS Axial load (kN)',value =2500)
with m_column:    
    moment = st.number_input(label='ULS Moment (kNm)',value =21000)
with v_column:  
    shear = st.number_input(label='ULS Shear (kN)',value =220)

st.header('Wall dimensions')
t_column, l_column = st.beta_columns(2)
with t_column:
    t = st.number_input(label='Enter wall thickness (mm)',value =200)
with l_column:
    l_w = st.number_input(label='Enter wall length (mm)', value = 3000)
    


st.header('Concrete')
fc_column, c_column = st.beta_columns(2)
with fc_column:
    f_c = st.number_input(label='Compression strength (MPa)', value = 40)
with c_column:
    c_end = st.number_input(label='Cover to steel (mm)', value = 40)

st.header('Reo')
v_column, h_column, s_column = st.beta_columns(3)
with v_column:
    st.subheader('Vertical steel')
    d_bl = st.selectbox(label= 'Dia vertical steel (mm)', options = BAR_SIZES)
    f_y = st.number_input(label='Vert reo yield strength (MPa)', value = 500)
    s_v = st.number_input(label='Spacing of vertical bars (mm)', value = 300)
    n_l = st.number_input(label='Number of layers steel', value =2)
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
    d_s=8,
    s_v=s_v,
    n_l=n_l,
    c_end=c_end
)

fig = go.Figure(data = go.Scatter(x = m,y=n))

st.plotly_chart(fig, use_container_width= True)





