import streamlit as st
import pandas as pd
import numpy as np
from scipy import spatial
import plotly.graph_objects as go
from pathlib import Path
import platform

############
### PATH ###
############

if platform.system() == 'Darwin':
    main_path = Path(".")
    logo_path = Path(".")
else:
    main_path = Path("RRSim")
    logo_path = Path("RRSim")

############
### FIS ####
############

FIS_path = str(main_path.joinpath('RR_FIS.fld'))

def Q1_to_num(answer):
    if answer == 'High': result = 1
    if answer == 'Medium': result = 0.5
    if answer == 'Low': result = 0
    return result

def Q2_to_num(answer):
    if answer == 'Extreme': result = 1
    if answer == 'Moderate': result = 0.5
    if answer == 'Low': result = 0
    return result

def Q3_to_num(answer):
    if answer == 'Deliberate': result = 1
    if answer == 'Ignorant': result = 0.5
    if answer == 'Accidental': result = 0
    return result

def Q4_to_num(answer):
    if answer == 'Repeat': result = 1
    if answer == 'First': result = 0
    return result

def Q5_to_num(answer):
    if answer == 'Unable': result = 1
    if answer == 'Uncertain': result = 0.5
    if answer == 'Able': result = 0
    return result

def Q6_to_num(answer):
    if answer == 'Unwilling': result = 1
    if answer == 'Undecided': result = 0.5
    if answer == 'Willing': result = 0
    return result

def Q7_to_num(answer):
    if answer == 'Yes': result = 1
    if answer == 'Unsure': result = 0.5
    if answer == 'No': result = 0
    return result

# READ FILE:
df_FIS = pd.read_csv(FIS_path, sep='\s', engine='python')
df_FIS_in = df_FIS.iloc[:, :-1]
df_FIS_in = df_FIS_in.to_numpy()
df_FIS_out = df_FIS.iloc[:, df_FIS.shape[1] - 1]

# NORMALISE 0-1
a, b = 0, 1
x, y = df_FIS_out.min(), df_FIS_out.max()
df_FIS_out = (df_FIS_out - x) / (y - x) * (b - a) + a

# GENERATE TREE:
tree_FIS = spatial.KDTree(data = df_FIS_in, copy_data = True)

def fis(input_list):
    '''
    Parameters
    ----------
    
    Returns
    -------
    list
    '''
    legislative_guidance = input_list[0]
    risk_assessment = input_list[1]
    attitude_offence = input_list[2]
    compliance_history = input_list[3]
    ability_remedial = input_list[4]
    attitude_following = input_list[5]
    persistence_noncompliance = input_list[6]
    
    # INTERPOLATION - FIS
    result = []
    
    idx = tree_FIS.query(
        x = [
            legislative_guidance,
            risk_assessment,
            attitude_offence,
            compliance_history,
            ability_remedial,
            attitude_following,
            persistence_noncompliance])[1]
    
    result = df_FIS_out.loc[idx]  
    
    return result

###########

if "df" not in st.session_state:
    column_names = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Low","High","Threshold","RRSim"]
    st.session_state.df = pd.DataFrame(columns = column_names)

apptitle = 'Responsive Regulation Simulator'

st.set_page_config(page_title=apptitle, layout="wide", page_icon=":eyeglasses:")

st.sidebar.image(str(logo_path.joinpath('RRSim logo.png')))
st.sidebar.markdown('This simulator is a learning tool that helps understand responsive regulation in regulatory systems. It should not be used or applied as a definitive responsive regulation tool in the workplace.')

st.sidebar.markdown('## User Inputs')

if st.sidebar.button("Reset values", key=None, help="press this button to reset the trajectory table and trajectory plot", on_click=None):
    column_names = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Low","High","Threshold","RRSim"]
    st.session_state.df = pd.DataFrame(columns = column_names)

with st.sidebar.form(key ='Form1'):
    
    st.subheader("Case Study Context")
    
    option_1 = st.selectbox('Q1: What level of regulatory intervention does the policy allow for?',('High', 'Medium', 'Low'), key=1)

    option_2 = st.selectbox('Q2: What is the actual or potential risk assessment in terms of impact of non-compliance?',('Extreme', 'Moderate', 'Low'), key=2)

    option_3 = st.selectbox('Q3: What is the attitude and behaviour of the regulated entity leading to the non-compliance?',('Deliberate', 'Ignorant', 'Accidental'), key=3)

    option_4 = st.selectbox('Q4: What is the compliance history?',('Repeat', 'First'), key=4)

    option_5 = st.selectbox('Q5: What is the ability of the regulated entity to take remedial action?',('Unable', 'Uncertain', 'Able'), key=5)

    option_6 = st.selectbox('Q6: What is the attitude and behaviour of the regulated entity during or following the initiation of regulatory action?',('Unwilling', 'Undecided','Willing'), key=6)

    option_7 = st.selectbox('Q7: Does non-compliance persist?',('Yes', 'Unsure', 'No'), key=7)
        
    st.subheader("Your estimate")
    
    values = st.slider('What compliance responses should be undertaken (select a range; this will displayed in grey within the gauge)?',0, 100, (25, 75))
        
    st.subheader("Your threshold")
    
    threshold = st.slider('What would you accept as the minimum level of response in this context (this will be displayed as a red line in the gauge)?',0, 100, 80)
    
    ### convert answers to float
    
    option_1_num = Q1_to_num(option_1)
    option_2_num = Q2_to_num(option_2)
    option_3_num = Q3_to_num(option_3)
    option_4_num = Q4_to_num(option_4)
    option_5_num = Q5_to_num(option_5)
    option_6_num = Q6_to_num(option_6)
    option_7_num = Q7_to_num(option_7)
   
    RR_result = fis([option_1_num,option_2_num,option_3_num,option_4_num,option_5_num,option_6_num,option_7_num])

    if st.form_submit_button("Submit 👍🏼"):
        
        to_append = [option_1,option_2,option_3,option_4,option_5,option_6,option_7,values[0],values[1],threshold,int(RR_result*100)]
        a_series = pd.Series(to_append, index = st.session_state.df.columns)
 
        st.session_state.df = st.session_state.df.append(a_series, ignore_index=True)
              
st.sidebar.markdown('## About RESPONSim')

with st.sidebar.expander("About"):
     st.write("""
         The reasoning that underpins this simulation is informed by the inputs of a range of regulatory experts through the application of Fuzzy Logic rules
     """)
        
def update_gauge():

    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = int(RR_result*100),
        number = { 'suffix': '%' },
        mode = "gauge+number",
        title = {'text': "What compliance response should be adopted?", 'font': {'size': 30}},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [None, 100]},
                 'steps' : [
                     {'range': [0, values[0]], 'color': "white"},
                     {'range': [values[0], values[1]], 'color': "gray"}],
                    
                 'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': threshold}}))

    fig.update_layout(width=500, height=700)
    fig.update_traces(gauge_axis_tickmode = 'array',
                      gauge_axis_tickvals = [0, 100/8*1, 100/8*2, 100/8*3, 100/8*4, 100/8*5, 100/8*6, 100/8*7, 100],
                      gauge_axis_ticktext = ['Awareness (0%)', 'Education (12.5%)', 'Counselling (25%)', 'Infringement (37.5%)', 'Undertakings (50%)', 'Direction (62.5%)','Order (75%)','Injunction (87.5%)','Prosecution (100%)'])
    fig.update_layout(font=dict(size=13))

    st.plotly_chart(fig, use_container_width=True)        
        
update_gauge()
        
col1, col2 = st.columns(2)

data = np.random.randn(10, 1).astype(int)

with col1:
    st.subheader("Trajectory table")
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    st.dataframe(st.session_state.df)
    
with col2:
    st.subheader("Trajectory plot")
    
    rrsim_trace_x = st.session_state.df.index.tolist()
    rrsim_trace_y = st.session_state.df.RRSim.to_numpy()

    low_trace_x = st.session_state.df.index.tolist()
    low_trace_y = st.session_state.df.Low.to_numpy()

    high_trace_x = st.session_state.df.index.tolist()
    high_trace_y = st.session_state.df.High.to_numpy()
    
    threshold_trace_x = st.session_state.df.index.tolist()
    threshold_trace_y = st.session_state.df.Threshold.to_numpy()

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=low_trace_x, y=low_trace_y, fill=None, mode='lines', line_color='grey', name='low estimate'))
    fig.add_trace(go.Scatter(x=high_trace_x, y=high_trace_y, fill='tonexty', mode='lines', line_color='grey', name='high estimate'))
    fig.add_trace(go.Scatter(x=rrsim_trace_x, y=rrsim_trace_y, fill=None, mode='lines+markers', line_color='darkgreen', line_width=8 ,name='RRSim'))
    fig.add_trace(go.Scatter(x=threshold_trace_x, y=threshold_trace_y, fill=None, mode='lines', line_color='red', line_width=4, name='Threshold'))

    config = {'staticPlot': True}

    fig.update_layout(
    showlegend=True,
    yaxis=dict(
        type='linear',
        range=[0, 100],
        ticksuffix='%'))
    
    fig.update_layout(font=dict(size=13))
   
    st.plotly_chart(fig, use_container_width=False, config=config)
    

