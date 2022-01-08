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
    #df_us = pd.read_csv('https://github.com/nytimes/covid-19-data/blob/master/rolling-averages/us.csv')
    df_state = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-states.csv',parse_dates=['date'])
    df_state['fips'] = df_state.geoid.apply(lambda x: x.split('-')[1])
    states = df_state.state.unique().tolist()
    states.sort()
    date_list = df_state.date.unique()
    state_fips = pd.read_csv('data/state_fips.csv')
    state_fips_dict = dict(zip(state_fips.state, state_fips.fips))
    return df_state, states, date_list,state_fips_dict



# --- Load data -----
df_state, states, date_list,state_fips_dict = load_data()


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
col_name=st.selectbox('',('cases','cases_avg','cases_avg_per_100k','deaths','deaths_avg','deaths_avg_per_100k'))

date_min = df_state.date.min()
date_max = df_state.date.max()

st.markdown("---")

#--- map of daily new cases ---

st.markdown("## Evolution Map")

with open('data/us-states.json') as response_new:
    state_json = json.load(response_new)

#date_map_test = st.slider("choose a date",date_min, date_max)
date_map= st.slider("Choose a date",date_min, date_max, value=default_starting_date,key='date_map')
df_state_map = df_state.query('date == @date_map')
color_high = df_state_map.loc[:,col_name].max()
color_low = df_state_map.loc[:,col_name].min()
fig_map = px.choropleth_mapbox(df_state_map, geojson=state_json, locations='fips', color=col_name, color_continuous_scale="Viridis", range_color=(color_low, color_high),mapbox_style="carto-positron", zoom=2.8, center = {"lat": 37.0902, "lon": -95.7129},opacity=1,hover_name='state')

fig_map.update_layout(width=700,height=400,margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map)


#----------------------All state Acceleration -------------
st.markdown('---')
# All states mean acceleration plot
st.markdown("## Average Acceleration over the Selected Period")

#layout_col1,layout_col2 = st.beta_columns(2)
#start_date = layout_col1.slider("Choose Starting Date",date_min, date_max, value=default_starting_date,key='start_date')
#end_date = layout_col2.slider("Choose Ending Date", date_min, date_max,value=default_ending_date,key='end_date')

start_date, end_date = st.slider("Choose a Time Range", date_min,date_max,value=(default_starting_date,default_ending_date),key='time_range')
st.markdown(f'Selected time range is from {start_date} to {end_date}')

dff = df_state.query('date >= @start_date and date <= @end_date').groupby('state').apply(lambda g: g.loc[:,col_name].diff().mean())

# display bar chart
fig_acc1 = px.bar(dff[0:25],labels={'value':'Mean '+col_name+' Acceleration','state':''})
fig_acc1.update_layout(width=770,showlegend=False)
fig_acc2 = px.bar(dff[25:],labels={'value':'Mean '+col_name+' Acceleration','state':''})
fig_acc2.update_layout(width=770,showlegend=False)
st.plotly_chart(fig_acc1)
st.plotly_chart(fig_acc2)


# ----- Specific states EPI and Acceleration ------
st.markdown('---')
st.markdown("## Comparisons across States")
select_state = st.multiselect('Choose One or More States',states,default=['New Jersey','California'])

start_date_state = st.slider("Choose Starting Date",date_min, date_max,value=default_8month_ago,key='start_date_state')
end_date_state = st.slider("Choose Ending Date", date_min, date_max,value=default_ending_date,key='end_date_state')



df_state_i = df_state.query('date >= @start_date_state & date <= @end_date_state & state in @select_state').loc[:,['date','state',col_name]].set_index('date')

def state_acceleration(dfi):
    dfi['acceleration'] = dfi.loc[:,col_name].diff()
    return dfi
df_state_i = df_state_i.groupby('state').apply(state_acceleration)



fig_state_epi = px.bar(df_state_i,y=col_name,color='state',labels={'value':'New '+col_name,'date':''})
fig_state_epi.update_layout(width=770,height=500,legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
))
fig_state_acc = px.line(df_state_i,y='acceleration',color='state',labels={'value':col_name+' Acceleration','date':''})

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
