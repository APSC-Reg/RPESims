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
    main_path = Path("DDMSim")
    logo_path = Path("DDMSim")

############
### FIS ####
############

FIS_path = str(main_path.joinpath('DDM_FIS.fld'))

def YMN_to_num(answer):
    if answer == 'Yes': result = 1
    if answer == 'Maybe': result = 0.5
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
    facts_relevant = input_list[0]
    facts_credible = input_list[1]
    facts_sufficient = input_list[2]
    decisions_documented = input_list[3]
    conclusions_reasonable = input_list[4]
    applying_policy = input_list[5]
    decision_within = input_list[6]
    discretion_level = input_list[7]
    processes_fair = input_list[8]
    
    # INTERPOLATION - FIS
    result = []
    
    idx = tree_FIS.query(
        x = [
            facts_relevant,
            facts_credible,
            facts_sufficient,
            decisions_documented,
            conclusions_reasonable,
            applying_policy,
            decision_within,
            discretion_level,
            processes_fair])[1]
    
    result = df_FIS_out.loc[idx]  
    
    return result

###########

if "df" not in st.session_state:
    column_names = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Low","High","Threshold","DDMSim"]
    st.session_state.df = pd.DataFrame(columns = column_names)

apptitle = 'Defensible Decision Making Simulator'

st.set_page_config(page_title=apptitle, layout="wide", page_icon=":eyeglasses:")

st.sidebar.image(str(logo_path.joinpath('DDMSim logo.png')))
st.sidebar.markdown('This simulator is a learning tool that helps understand defensible decision making in regulatory systems. It should not be used or applied as a definitive decision making tool in the workplace.')

st.sidebar.markdown('## User Inputs')

if st.sidebar.button("Reset values", key=None, help="press this button to reset the trajectory table and trajectory plot", on_click=None):
    column_names = ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","Low","High","Threshold","DDMSim"]
    st.session_state.df = pd.DataFrame(columns = column_names)

with st.sidebar.form(key ='Form1'):
    
    st.subheader("Case Study Context")
    
    option_1 = st.selectbox('Q1: Are the facts relevant?',('Yes', 'Maybe', 'No'), key=1)

    option_2 = st.selectbox('Q2: Are the facts credible?',('Yes', 'Maybe', 'No'), key=2)

    option_3 = st.selectbox('Q3: Are the facts sufficient?',('Yes', 'Maybe', 'No'), key=3)

    option_4 = st.selectbox('Q4: Are the decisions leading to conclusions documented in a clear and consistent way?',('Yes', 'Maybe', 'No'), key=4)

    option_5 = st.selectbox('Q5: Are the conclusions drawn from the evidence reasonable and rational?',('Yes', 'Maybe', 'No'), key=5)

    option_6 = st.selectbox('Q6: Are you applying the policy correctly and with discretion?',('Yes', 'Maybe', 'No'), key=6)

    option_7 = st.selectbox('Q7: Is the decision within limits of the source of power?',('Yes', 'Maybe', 'No'), key=7)

    option_8 = st.selectbox('Q8: Does it give you discretion?',('Broad', 'Limited', 'Nil'), key=8)

    option_9 = st.selectbox('Q9: Are the processes and procedures fair and impartial?',('Yes', 'Maybe', 'No'), key=9)
        
    st.subheader("Your estimate")
    
    values = st.slider('How defensible do you think the decision is (select a range; this will displayed in grey within the gauge)?',0, 100, (25, 75))
    
    value = np.random.randint(low=0, high=100)
    
    st.subheader("Your threshold")
    
    threshold = st.slider('What would you accept as the minimum level of confidence (this will be displayed as a red line in the gauge)?',0, 100, 80)
    
    ### convert answers to float
    
    option_1_num = YMN_to_num(option_1)
    option_2_num = YMN_to_num(option_2)
    option_3_num = YMN_to_num(option_3)
    option_4_num = YMN_to_num(option_4)
    option_5_num = YMN_to_num(option_5)
    option_6_num = YMN_to_num(option_6)
    option_7_num = YMN_to_num(option_7)
    option_9_num = YMN_to_num(option_9)
    
    if option_8 == 'Broad': option_8_num = 1
    if option_8 == 'Limited': option_8_num = 0.5
    if option_8 == 'Nil': option_8_num = 0
   
    DDM_result = fis([option_1_num,option_2_num,option_3_num,option_4_num,option_5_num,option_6_num,option_7_num,option_8_num,option_9_num])

    if st.form_submit_button("Submit 👍🏼"):
        
        to_append = [option_1,option_2,option_3,option_4,option_5,option_6,option_7,option_8,option_9,values[0],values[1],threshold,int(DDM_result*100)]
        a_series = pd.Series(to_append, index = st.session_state.df.columns)
 
        st.session_state.df = st.session_state.df.append(a_series, ignore_index=True)
              
st.sidebar.markdown('## About DDMSim')

with st.sidebar.expander("About"):
     st.write("""
         The reasoning that underpins this simulation is informed by the inputs of a range of regulatory experts through the application of Fuzzy Logic rules
     """)
        
def update_gauge():

    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = int(DDM_result*100),
        number = { 'suffix': '%' },
        mode = "gauge+number",
        title = {'text': "Is this decision defensible?", 'font': {'size': 30}},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [None, 100]},
                 'steps' : [
                     {'range': [0, values[0]], 'color': "white"},
                     {'range': [values[0], values[1]], 'color': "gray"}],
                    
                 'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': threshold}}))

    fig.update_layout(width=500, height=700)
    fig.update_traces(gauge_axis_tickmode = 'array',
                      gauge_axis_tickvals = [0, 50, 100],
                      gauge_axis_ticktext = ['No (0%)', 'Maybe (50%)', 'Yes (100%)'])
    
    fig.update_layout(font=dict(size=10))

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
    
    ddmsim_trace_x = st.session_state.df.index.tolist()
    ddmsim_trace_y = st.session_state.df.DDMSim.to_numpy()

    low_trace_x = st.session_state.df.index.tolist()
    low_trace_y = st.session_state.df.Low.to_numpy()

    high_trace_x = st.session_state.df.index.tolist()
    high_trace_y = st.session_state.df.High.to_numpy()
    
    threshold_trace_x = st.session_state.df.index.tolist()
    threshold_trace_y = st.session_state.df.Threshold.to_numpy()

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=low_trace_x, y=low_trace_y, fill=None, mode='lines', line_color='grey', name='low estimate'))
    fig.add_trace(go.Scatter(x=high_trace_x, y=high_trace_y, fill='tonexty', mode='lines', line_color='grey', name='high estimate'))
    fig.add_trace(go.Scatter(x=ddmsim_trace_x, y=ddmsim_trace_y, fill=None, mode='lines+markers', line_color='darkgreen', line_width=8, name='DDMSim'))
    fig.add_trace(go.Scatter(x=threshold_trace_x, y=threshold_trace_y, fill=None, mode='lines', line_color='red', line_width=4, name='Threshold'))


    config = {'staticPlot': True}

    fig.update_layout(
    showlegend=True,
    yaxis=dict(
        type='linear',
        range=[0, 100],
        ticksuffix='%'))
    
    fig.update_layout(font=dict(size=10))
    
    st.plotly_chart(fig, use_container_width=False, config=config)
    

