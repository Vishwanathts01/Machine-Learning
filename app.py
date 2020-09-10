import numpy as np
import json 
import requests
import pandas as pd
import datetime
import dash_table
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from scipy.integrate import odeint
from scipy.optimize import curve_fit

def data():
    data_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    data_confirmed = data_confirmed.drop(["Province/State", "Lat", "Long"], axis =1)
    data_confirmed = data_confirmed.groupby(["Country/Region"]).sum()

    recovered_data=pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
    recovered_data=recovered_data.drop(["Province/State","Lat", "Long"],axis=1)
    recovered_data = recovered_data.groupby(["Country/Region"]).sum()

    deaths_data=pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
    deaths_data=deaths_data.drop(["Province/State","Lat", "Long"],axis=1)
    deaths_data = deaths_data.groupby(["Country/Region"]).sum()

    return data_confirmed, recovered_data, deaths_data 

def data_table():

    data_confirmed, recovered_data, deaths_data = data()

    last_date = deaths_data.T.index[-1]
    data_table = pd.DataFrame([data_confirmed[last_date], recovered_data[last_date], deaths_data[last_date]]).T
    data_table.columns = ["confirmed", "recovered", "deaths"]
    data_table["active"] = data_table.confirmed - data_table.recovered - data_table.deaths
    data_table ["percent_deaths"] = np.round(data_table.deaths / data_table.confirmed, 2)
    data_table ["percent_recoveries"] = np.round(data_table.recovered / data_table.confirmed, 2)
    data_table = data_table.sort_values(by = 'confirmed', ascending = False)
    data_table.reset_index(level=0, inplace=True)

    return data_table

def sir_simulations( confirmed_data, recovered_data, dates):
 
    duration_for_simulation = 30 # duration for simulations 

    confirmed_data = confirmed_data[(len(confirmed_data)-duration_for_simulation):]

    recovered_data = recovered_data[(len(recovered_data)- duration_for_simulation):]

    dates = dates[ len(dates)-duration_for_simulation: ]
    N = 1000000
    I_0 = confirmed_data[0]
    R_0 = recovered_data[0]
    S_0 = N - R_0 - I_0

    def SIR(y, t, beta, gamma):    
        S = y[0]
        I = y[1]
        R = y[2]
        return -beta*S*I/N, (beta*S*I)/N-(gamma*I), gamma*I

    def fit_odeint(t,beta, gamma):
        return odeint(SIR,(S_0,I_0,R_0), t, args = (beta,gamma))[:,1]

    t = np.arange(len(confirmed_data))
    params, cerr = curve_fit(fit_odeint,t, confirmed_data)
    beta,gamma = params
    prediction = list(fit_odeint(t,beta,gamma))


    fig = go.Figure()
    fig.add_trace(go.Scatter(x= dates, y= prediction,
                        mode='lines+markers',
                        name='Simulated'))
    fig.add_bar(x = dates, y= confirmed_data, name = "Actual")
    fig.update_layout(height = 800,
    title={
        'text':"SIR simulations",
        'x' : 0.5},
    xaxis_title="Date",
    yaxis_title="Infections")

    return fig



app = dash.Dash(__name__, suppress_callback_exceptions=True)
server=app.server

df = data_table()
confirmed_data, recovered_data, deaths_data = data()
str_dates = confirmed_data.columns
start_date = str_dates[0].split('/')
end_date = str_dates[-1].split('/')
if len(end_date[0]) == 1: 
    dates = np.arange(np.datetime64(f'20{start_date[2]}-0{start_date[0]}-{start_date[1]}'), np.datetime64(f'20{end_date[2]}-0{end_date[0]}-{int(end_date[1])+1}'))
else:
    dates = np.arange(np.datetime64(f'20{start_date[2]}-0{start_date[0]}-{start_date[1]}'), np.datetime64(f'20{end_date[2]}-{end_date[0]}-{int(end_date[1])+1}'))

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])




## Global data Layout

index_page = html.Div([
    html.H2("COVID-19 Dashboard", style = {'textAlign' : 'center'}),

    html.Table(
        html.Tr(
            [
                html.Td(dcc.Link(html.Button('global',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/global_data' )),
                html.Td(
                    dcc.Link(html.Button('country data',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/country_data')
                ),
                html.Td(
                    dcc.Link(html.Button('comparision',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/country_comparision' )
                )
            ]
        ), style = { 'width' : '80%' , 'marginLeft' : '10%',  'textAlign' : 'center'}
    ),
    html.Br(),
    html.Br(),
    
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    style_cell={
        'height': 'auto',

        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        'whiteSpace': 'normal',
        'textAlign' : 'center'

        
    },
    style_table={
        'width': '800px',
        'marginLeft' : '8%',
    },
),
    
])

# country wise data layout 

country_data_layout = html.Div([
    html.H2("COVID-19 Dashboard", style = {'textAlign' : 'center'}),
     html.Table(
        html.Tr(
            [
                html.Td(dcc.Link(html.Button('global',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/global_data' )),
                html.Td(
                    dcc.Link(html.Button('country data',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/country_data')
                ),
                html.Td(
                    dcc.Link(html.Button('comparision',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/country_comparision' )
                )
            ]
        ), style = { 'width' : '80%' , 'marginLeft' : '10%', 'textAlign' : 'center'}
    ),
    html.Br(),
    html.Br(),

    html.Div([
        dcc.Dropdown(
        id="country_list",
        options=[ {'label':country_name , 'value': country_name } for country_name in list(confirmed_data.index)],
        value='Germany'
    ),
    ]),
    html.Div(dcc.Graph(id = 'confirmed_cases_country')),
    html.Div(dcc.Graph(id = 'recovered_cases_country')),
    html.Div(dcc.Graph(id = 'deaths_cases_country')),
    html.Div(dcc.Graph(id = 'sir_simulations_country'))
])

@app.callback(
    [Output ( 'confirmed_cases_country' , 'figure'),
    Output ( 'recovered_cases_country' , 'figure'),
    Output ( 'deaths_cases_country' , 'figure'), 
    Output ( 'sir_simulations_country' , 'figure')  ],
    [Input('country_list', 'value' )],
    )

def country_data(country):

    confirmed_cases =  list(confirmed_data.loc[f'{country}'])
    recovered_cases =  list(recovered_data.loc[f'{country}'])
    death_cases = list(deaths_data.loc[f'{country}'])

    sir_figure = sir_simulations( confirmed_cases, recovered_cases, dates)

    confirmed = px.line(x = dates ,y = confirmed_cases , labels = { "x" : "Date", "y" : "Confirmed cases"}, height = 800)
    confirmed.update_layout(title_text = " Confirmed cases" ,title_x=0.5 )


    recovered = px.line(x = dates ,y = recovered_cases , labels = { "x" : "Date", "y" : "Recovered cases"}, height = 800)
    recovered.update_layout(title_text = " Recovered cases" ,title_x=0.5)

    deaths = px.line(x = dates ,y = death_cases , labels = { "x" : "Date", "y" : "Deaths"} ,height = 800)
    deaths.update_layout(title_text = " Deaths" ,title_x=0.5 )

    return confirmed, recovered, deaths, sir_figure


# countrywise comparision 

comparision_layout = html.Div([
    html.H2("COVID-19 Dashboard", style = {'textAlign' : 'center'}),
     html.Table(
        html.Tr(
            [
                html.Td(dcc.Link(html.Button('global',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/global_data' )),

                html.Td(
                    dcc.Link(html.Button('country data',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/country_data')
                ),
                html.Td(
                    dcc.Link(html.Button('comparision',  style = {
        'backgroundColor': '#008080',
        'border': 'none',
        'color': 'white',
        'padding': '15px 32px',
        'textAlign': 'center',
        'textDecoration': 'none',
        'display': 'inlineBlock',
        'fontSize': '16px',
        'borderRadius': '8px'
    }), href='/country_comparision' )
                )
            ]
        ), style = { 'width' : '80%' , 'marginLeft' : '10%' , 'textAlign' : 'center'}
    ),
    html.Br(),
    html.Br(),

    html.Div([
    dcc.Dropdown(
        id='comparision_countries',
        options=[ {'label':country_name , 'value': country_name } for country_name in list(confirmed_data.index)],
        value=['Germany', 'India'],
        multi = True,
    ),
]),
    html.Div(dcc.Graph(id = 'confirmed_comparision')),
    html.Div(dcc.Graph(id = 'recovered_comparision')),
    html.Div(dcc.Graph(id = 'death_comparision')),
])

@app.callback(
    [Output('confirmed_comparision' , 'figure'),
    Output('recovered_comparision' , 'figure'),
    Output('death_comparision' , 'figure')],
    [Input('comparision_countries', 'value')]
)
def comparision_countries_logic(comparision_countries):
    confirmed_figure = go.Figure()
    recovered_figure = go.Figure()
    death_figure = go.Figure()

    for each in comparision_countries:
        confirmed_figure.add_traces( go.Scatter(x= dates, y =list(confirmed_data.loc[f'{each}']), mode='lines+markers', name = each))
        recovered_figure.add_traces( go.Scatter(x= dates, y =list(recovered_data.loc[f'{each}']), mode='lines+markers', name = each))
        death_figure.add_traces( go.Scatter(x= dates, y =list(deaths_data.loc[f'{each}']), mode='lines+markers', name = each))


    confirmed_figure.update_layout(title ={'text' : 'Confirmed Cases Comparision','x' : 0.5 },
    xaxis_title="Date",
    yaxis_title="Infections",
    height = 800
    )

    recovered_figure.update_layout(title =
    {'text' : 'Recovered Cases Comparision',
     'x' : 0.5 },
    xaxis_title="Date",
    yaxis_title="Reecoveries",
    height = 800
    )

    death_figure.update_layout(title =
    {'text' : 'Deaths Comparision',
     'x' : 0.5 },
    xaxis_title="Date",
    yaxis_title="Deaths",
    height = 800
    )

    return confirmed_figure, recovered_figure, death_figure
    

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/country_data':
        return country_data_layout
    elif pathname == '/country_comparision':
        return comparision_layout
    else:
        return index_page


if __name__ == '__main__':
    app.run_server(debug=True)
