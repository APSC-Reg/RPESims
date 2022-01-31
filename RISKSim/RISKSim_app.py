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
    main_path = Path("RISKSim")
    logo_path = Path("RISKSim")

############
### FIS ####
############

FIS_path = str(main_path.joinpath('RISK_FIS.fld'))

def YMN_to_num(answer):
    if answer == 'Yes': result = 1
    if answer == 'Maybe': result = 0.5
    if answer == 'No': result = 0
    return result

def LIKELIHOOD_to_num(answer):
    if answer == 'Rare': result = 0
    if answer == 'Unlikely': result = 0.25
    if answer == 'Possible': result = 0.5
    if answer == 'Likely': result = 0.75
    if answer == 'Probable': result = 1
    return result

def CONSEQUENCE_to_num(answer):
    if answer == 'Negligible': result = 0
    if answer == 'Minor': result = 0.25
    if answer == 'Moderate': result = 0.5
    if answer == 'Major': result = 0.75
    if answer == 'Catastrophic': result = 1
    return result

# READ FILE:
df_FIS = pd.read_csv(FIS_path, sep='\s', engine='python')
df_FIS_in = df_FIS.iloc[:, :-1]
df_FIS_in = df_FIS_in.to_numpy()
df_FIS_out = df_FIS.iloc[:, df_FIS.shape[1] - 1]
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
    identified_risk = input_list[0]
    industry_acceptance = input_list[1]
    community_acceptance = input_list[2]
    clear_understanding = input_list[3]
    process_identify = input_list[4]
    likelihood_rating = input_list[5]
    consequence_rating = input_list[6]
    
    # INTERPOLATION - FIS
    result = []
    
    idx = tree_FIS.query(
        x = [
            identified_risk,
            industry_acceptance,
            community_acceptance,
            clear_understanding,
            process_identify,
            likelihood_rating,
            consequence_rating])[1]
    
    result = df_FIS_out.loc[idx]  
    
    return result

###########

if "df" not in st.session_state:
    column_names = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Low","High","Threshold","RISKSim"]
    st.session_state.df = pd.DataFrame(columns = column_names)

apptitle = 'Risk Management Simulator'

st.set_page_config(page_title=apptitle, layout="wide", page_icon=":eyeglasses:")

st.sidebar.image(str(logo_path.joinpath('RISKSim logo.png')))
st.sidebar.markdown('This simulator is a learning tool that helps understand risk management in regulatory systems. It should not be used or applied as a definitive risk management tool in the workplace.')

st.sidebar.markdown('## User Inputs')

if st.sidebar.button("Reset values", key=None, help="press this button to reset the trajectory table and trajectory plot", on_click=None):
    column_names = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Low","High","Threshold","RISKSim"]
    st.session_state.df = pd.DataFrame(columns = column_names)

with st.sidebar.form(key ='Form1'):
    
    st.subheader("Case Study Context")
    
    option_1 = st.selectbox('Q1: Have you identified the main risk you are trying to reduce, avoid or mitigate?',('Yes', 'Maybe', 'No'), key=1)

    option_2 = st.selectbox('Q2: Industry acceptance and support for the risk setting?',('Yes', 'Maybe', 'No'), key=2)

    option_3 = st.selectbox('Q3: Community acceptance and support for the risk setting?',('Yes', 'Maybe', 'No'), key=3)

    option_4 = st.selectbox('Q4: Clear understanding of your agency risk appetite?',('Yes', 'Maybe', 'No'), key=4)

    option_5 = st.selectbox('Q5: Process to identify risk rigorous, repeatable, verifiable?',('Yes', 'Maybe', 'No'), key=5)

    option_6 = st.selectbox('Q6: Likelihood?',('Rare', 'Unlikely','Possible','Likely','Probable'), key=6)

    option_7 = st.selectbox('Q7: Consequence?',('Negligible','Minor','Moderate','Major','Catastrophic'), key=7)
        
    st.subheader("Your guess")
    
    values = st.slider('What level of risk management should be adopted (select a range; this will displayed in grey within the gauge)?',0, 100, (25, 75))
    
    value = np.random.randint(low=0, high=100)
    
    st.subheader("Your threshold")
    
    threshold = st.slider('What would you accept as the minimum level of risk management (this will be displayed as a red line in the gauge)?',0, 100, 80)
    
    ### convert answers to float
    
    option_1_num = YMN_to_num(option_1)
    option_2_num = YMN_to_num(option_2)
    option_3_num = YMN_to_num(option_3)
    option_4_num = YMN_to_num(option_4)
    option_5_num = YMN_to_num(option_5)
    option_6_num = LIKELIHOOD_to_num(option_6)
    option_7_num = CONSEQUENCE_to_num(option_7)
   
    RISK_result = fis([option_1_num,option_2_num,option_3_num,option_4_num,option_5_num,option_6_num,option_7_num])

    if st.form_submit_button("Submit 👍🏼"):
        
        to_append = [option_1,option_2,option_3,option_4,option_5,option_6,option_7,values[0],values[1],threshold,int(RISK_result*100)]
        a_series = pd.Series(to_append, index = st.session_state.df.columns)
 
        st.session_state.df = st.session_state.df.append(a_series, ignore_index=True)
              
st.sidebar.markdown('## About RISKSim')

with st.sidebar.expander("About"):
     st.write("""
         The reasoning that underpins this simulation is informed by the inputs of a range of regulatory experts through the application of Fuzzy Logic rules
     """)
        
def update_gauge():

    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = int(RISK_result*100),
        number = { 'suffix': '%' },
        mode = "gauge+number",
        title = {'text': "What level of risk management should be adopted?", 'font': {'size': 30}},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [None, 100]},
                 'steps' : [
                     {'range': [0, values[0]], 'color': "white"},
                     {'range': [values[0], values[1]], 'color': "gray"}],
                    
                 'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': threshold}}))

    fig.update_layout(width=500, height=500)
    fig.update_traces(gauge_axis_tickmode = 'array',
                      gauge_axis_tickvals = [0, 20, 40, 60, 80, 100],
                      gauge_axis_ticktext = ['Avoid', 'Remove', 'Reduce Likelihood', 'Reduce Consequence', 'Share', 'Accept'])
    
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
    
    risksim_trace_x = st.session_state.df.index.tolist()
    risksim_trace_y = st.session_state.df.RISKSim.to_numpy()

    low_trace_x = st.session_state.df.index.tolist()
    low_trace_y = st.session_state.df.Low.to_numpy()

    high_trace_x = st.session_state.df.index.tolist()
    high_trace_y = st.session_state.df.High.to_numpy()
    
    threshold_trace_x = st.session_state.df.index.tolist()
    threshold_trace_y = st.session_state.df.Threshold.to_numpy()

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=low_trace_x, y=low_trace_y, fill=None, mode='lines', line_color='orange', name='low guess'))
    fig.add_trace(go.Scatter(x=high_trace_x, y=high_trace_y, fill='tonexty', mode='lines', line_color='orange', name='high guess'))
    fig.add_trace(go.Scatter(x=risksim_trace_x, y=risksim_trace_y, fill=None, mode='lines+markers', line_color='black', name='RISKSim'))
    fig.add_trace(go.Scatter(x=threshold_trace_x, y=threshold_trace_y, fill=None, mode='lines', line_color='red', name='Threshold'))


    config = {'staticPlot': True}

    fig.update_layout(
    showlegend=True,
    yaxis=dict(
        type='linear',
        range=[0, 100],
        ticksuffix='%'))
    
    st.plotly_chart(fig, use_container_width=False, config=config)
    

