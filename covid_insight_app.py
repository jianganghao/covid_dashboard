import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import json
import plotly.io as pio
pio.templates.default="ggplot2"



# --- define contant variables -----

today = datetime.date.today()
default_starting_date = today - datetime.timedelta(days=9)
default_ending_date = today - datetime.timedelta(days=2)
default_amonth_ago = today - datetime.timedelta(days=30)
default_8month_ago = today - datetime.timedelta(days=240)

# --- define functions -------

@st.cache(ttl=3600)
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',parse_dates=['date'])
    dft = df.pivot_table(values='cases', index='date',columns='state',aggfunc='sum').reset_index() # new cases
    dfd = df.pivot_table(values='deaths', index='date',columns='state',aggfunc='sum').reset_index() # death
    states = df.state.unique().tolist()
    states.sort()
    date_list = dft.index.tolist()
    state_fips = pd.read_csv('data/state_fips.csv')
    state_fips_dict = dict(zip(state_fips.state, state_fips.fips))
    return df, dft, dfd, states, date_list,state_fips_dict


@st.cache(ttl=3600)
def load_dictionary():
    state_fips = pd.read_csv('data/state_fips.csv',dtype={"fips":str})
    state_fips_dict = dict(zip(state_fips.state, state_fips.fips))
    return state_fips_dict

# --- Load data -----
#state_fips_dict = load_dictionary()
df, dft, dfd, states, date_list,state_fips_dict = load_data()


state_fips_dict = load_dictionary()


# Welcome to COVID-19 data insight

st.title("Welcome to COVID-19 Data Insight")

st.markdown("---")
st.markdown("## Dynamics matters")
st.markdown("Newton's second law of motion, _**F**_ = _**m**_ _**a**_, links the apparent position changes of an object to the force that leads to these changes, making it possible to undertand the underlying mechanism of the system and therefore predict the future of the changes. Here we draw a simple analogy, trying to understand the _**force**_ that drives the change of the numbers of COVID cases.")

st.markdown("The widely used [compartmental models in epidemiology](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology), such as the SRI model, are all based on the first order derivative of the number of cases and therefore they describe more about the _**kinematics**_. The ideas here are to consider the second order derivative to try to shed some light on the _**dynamics**_ of the changes of the numbers." )

st.markdown("The data used in this site is from [NY Times COVID-19 data](https://github.com/nytimes/covid-19-data). Please send your comments and suggestions to: [jianganghao@gmail.com](jianganghao@gmail.com)")
st.markdown("---")

# choose data
st.markdown("## First, Choose Data")
data_type=st.selectbox('',('Confirmed Cases', 'Confirmed Deaths'))

if data_type == "Confirmed Cases":
    dfx = dft
else:
    dfx = dfd

date_min = dfx.date.min()
date_max = dfx.date.max()

# ---  single state summary ---------
st.markdown("## Your State at A Glance")

#select_single_state = st.select_slider('Choose one State you want to get a Summary',states,value='New Jersey')
select_single_state = st.selectbox('Choose one State you want to get a Summary',states)

average_increase = dfx.query('date >= @default_starting_date & date <= @default_ending_date').loc[:,[select_single_state]].diff().mean().values[0]

average_acceleration = dfx.query('date >= @default_starting_date & date <= @default_ending_date').loc[:,[select_single_state]].diff().diff().mean().values[0]


current_total = dfx.query('date == @default_ending_date').loc[:,select_single_state].values[0]

st.markdown(f"### The total {data_type} as of {default_ending_date} is: **{round(current_total)}**")
st.markdown(f"In the week from {default_starting_date} to {default_ending_date}, in the State of {select_single_state}")
st.markdown(f"* The Average of new {data_type} of every day is: **{round(average_increase)}**")
st.markdown(f"* The Average acceleration of new {data_type} of every day is: **{round(average_acceleration)}**")



st.markdown("---")

#--- animation map of acceleration ---

st.markdown("## Evolution of Acceleration on A Map")
st.markdown("Based on 7-day rolling average acceleration of "+data_type)

with open('data/us-states.json') as response_new:
    state_json = json.load(response_new)

df_state_new = dfx.set_index('date').diff().diff().rolling(7).mean().stack().reset_index()
df_state_new.columns=['date','state','acceleration']
df_state_new['fips'] = df_state_new.state.replace(state_fips_dict).astype('str')

date_map= st.slider("Choose a date",date_min, date_max, value=default_starting_date,key='date_map')

if data_type == "Confirmed Cases":
    fig_map = px.choropleth_mapbox(df_state_new.query('date == @date_map'), geojson=state_json, locations='fips', color='acceleration', color_continuous_scale="Viridis", range_color=(-1000, 1000),mapbox_style="carto-positron", zoom=2.8, center = {"lat": 37.0902, "lon": -95.7129},opacity=1,hover_name='state')
else:
    fig_map = px.choropleth_mapbox(df_state_new.query('date == @date_map'), geojson=state_json, locations='fips', color='acceleration', color_continuous_scale="RdBu_r", range_color=(-50, 50),mapbox_style="carto-positron", zoom=2.8, center = {"lat": 37.0902, "lon": -95.7129},opacity=1,hover_name='state')
    

fig_map.update_layout(width=700,height=400,margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map)


#----------------------All state Acceleration -------------


st.markdown('---')
# All states mean acceleration plot
st.markdown("## Average Acceleration of All States")

#start_date = st.date_input("Choose Starting Date",default_starting_date)
start_date = st.slider("Choose Starting Date",date_min, date_max, value=default_starting_date,key='start_date')
end_date = st.slider("Choose Ending Date", date_min, date_max,value=default_ending_date,key='end_date')


# display bar chart
dff = dfx.query('date >= @start_date and date <= @end_date').set_index('date').diff().diff().mean()
fig_acc1 = px.bar(dff[0:25],labels={'value':'Mean '+data_type+' Acceleration','state':''})
fig_acc1.update_layout(width=770,showlegend=False)
fig_acc2 = px.bar(dff[25:],labels={'value':'Mean '+data_type+' Acceleration','state':''})
fig_acc2.update_layout(width=770,showlegend=False)
st.plotly_chart(fig_acc1)
st.plotly_chart(fig_acc2)






# ----- Specific states EPI and Acceleration ------
st.markdown('---')
st.markdown("## Comparisons across States")
select_state = st.multiselect('Choose One or More States',states,default=['New Jersey','California'])

start_date_state = st.slider("Choose Starting Date",date_min, date_max,value=default_8month_ago,key='start_date_state')
end_date_state = st.slider("Choose Ending Date", date_min, date_max,value=default_ending_date,key='end_date_state')



df_state = dfx.query('date >= @start_date_state & date <= @end_date_state').set_index('date').loc[:,select_state]
#df_state = dfx.query('date> @default_starting_date').set_index('date').loc[:,select_state]


fig_state_epi = px.bar(df_state.diff().round(),labels={'value':'New '+data_type,'date':''})
fig_state_epi.update_layout(width=770,height=500,legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))
fig_state_acc = px.area(df_state.diff().diff().rolling(7).mean(),labels={'value':data_type+' Acceleration','date':''})

fig_state_acc.update_layout(width=770,height=500,legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))

st.plotly_chart(fig_state_epi)
st.plotly_chart(fig_state_acc)

st.markdown("---")

st.markdown("## More is coming soon ...")
