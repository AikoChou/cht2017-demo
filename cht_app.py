import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py              ###
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask
import pandas as pd
import numpy as np
import os
import copy
import functools32

server = Flask('my app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('CHTApp', server=server, url_base_pathname='/cht2017', csrf_protect=False)

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })

external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "//fonts.googleapis.com/css?family=Raleway:400,300,600",
                "//fonts.googleapis.com/css?family=Dosis:Medium",
                "https://cdn.rawgit.com/plotly/dash-app-stylesheets/62f0eb4f1fadbefea64b2404493079bf848974e8/dash-uber-ride-demo.css",
                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

mapbox_access_token = 'pk.eyJ1IjoiYWlrb2Nob3UiLCJhIjoiY2o1bWF2emI4M2ZoYjJxbnFmbXFrdHQ0ZCJ9.w0_1-IC0JCPukFL7Bpa92w'

# Global map layout
layout = dict(
            showlegend = True,
            legend={'x': 0, 'y': 1},
            height=500,
            margin=Margin(l=0, r=0, t=0, b=0),
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=dict(
                    lat=25.032969,
                    lon=121.565418
                ),
                pitch=0,
                zoom=12,
                style='streets'
            ),
        )


def initialize():
    #--/* raw mode */--
    uid = "u_-35363411"
    raw_df = pd.read_csv('data/'+uid+'_raw.csv', dtype={'lon': str, 'lat': str})
    #--/* bus mode */--
    '''bus_output [-35363411,1483429279,1483430152,TPE15112,1,9,26]'''
    rid = 'TPE15112'
    direction = '1'
    s_idx = 9
    e_idx = 26
    trip_start_t = 1483429279
    trip_end_t = 1483430152
    df = pd.read_csv('data/bus_stop_infomation.csv', header=None,
                     names=['rid','route_name','direction','sid','stop_name','order','lon','lat'],
                     dtype=str)
    route_df = df[(df.rid==rid)&(df.direction ==direction)]
    route_df = route_df[(route_df.order.astype(int) >= s_idx)&(route_df.order.astype(int)<=e_idx)]

    prepro_df = pd.read_csv('data/'+uid+'_prepro.csv', dtype=str)
    user_ddf = prepro_df[(prepro_df.start_unix_t.astype(int) >= trip_start_t)&(prepro_df.end_unix_t.astype(int) <= trip_end_t)]

    return raw_df, prepro_df, route_df, user_ddf

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H2("Transportation Mode Detection App",
                style={'font-family': 'Dosis', 'float': 'left', 'position': 'relative', 'top': '30px', 'left': '10px'}),
            html.Img(src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe.png",
                style={
                    'height': '100px',
                    'float': 'right',
                    'position': 'relative',
                    'left': '5px'
                    },
            ),
            html.P("Public transportation mode detection with cellular data.\
                    Select different users and days using the dropdown and the slider\
                    below", className="explanationParagraph twelve columns",
                style={'float': 'left', 'position': 'relative', 'left': '15px'}),
        ], className='row'),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='my-dropdown',
                    options=[
                        {'label': 'Aiko', 'value': 'u_-35363411'},
                        {'label': 'Xiaochuan', 'value': 'u_-35363411'},
                        {'label': 'Chris', 'value': 'u_-35363411'},
                        {'label': 'Martin', 'value': 'u_-35363411'},
                        {'label': 'Sasha', 'value': 'u_-35363411'}
                    ],
                    value="u_-35363411",
                    placeholder="Please choose an user",
                    className="user-picker"
                ),
                html.Div([
                    dcc.RadioItems(
                        id='my-selector',
                        options=[
                            {'label': 'Raw Cellular Data ', 'value': 'raw'},
                            {'label': 'Preprocessed Data ', 'value': 'prepro'},
                            {'label': 'Mode Detection ', 'value': 'mode'}
                        ],
                        value='raw',
                        labelStyle={'display': 'inline-block'}
                    ),
                ],style={'margin-top': '10', 'margin-left': '7'})
            ],className='six columns'),
            html.Div([
                dcc.Dropdown(
                        id='multi-selector',
                        multi=True,
                        placeholder="This selector only showes when you choose mode detection.",
                ),
            ], className='six columns'),
        ], className='row'),
        html.Div([
            dcc.Graph(id='map-graph'),
        ])
    ], style={'margin': 'auto auto'}),
    html.Div([
        dcc.Slider(
            id="my-slider",
            marks = {i: ('Jan {}'.format(i) if i==1 or i==31 else '{}'.format(i)) for i in range(1, 32)},
            min=1,
            max=31,
            step=1,
            value=4
        ),
    ], style={'margin-top': '10'}),
    dcc.Markdown("Data Source: [ChunghwaTelecom](http://www.cht.com.tw/)",
             className="source"),
], className='ten columns offset-by-one')


def fetch_raw_dataframe(uid, date):
    return raw_df

def fetch_prepro_dataframe(uid, date):
    return prepro_df

def fetch_mode_dataframe(uid, date):
    return prepro_df, route_df, user_ddf

def get_detection_modes(uid, date):
    return ['Bus', 'Metro', 'HSR', 'Train']

@app.callback(Output('multi-selector', 'options'),[
                Input("my-dropdown", "value"), Input("my-slider", "value"),
                Input('my-selector', 'value'), ])
def set_selector_options(uid, date, selectedData):
    if selectedData == 'mode':
        options = get_detection_modes(uid, date)
        return [{'label': i, 'value': i.lower()} for i in options]
    else:
        return []

@app.callback(Output('multi-selector', 'value'),[
                Input("multi-selector", "options"), ])
def set_selector_value(available_options):
        return [ i['value'] for i in available_options]

@app.callback(Output("map-graph", "figure"),[
                Input("my-dropdown", "value"), Input("my-slider", "value"),
                Input("my-selector", "value")])
def update_graph(uid, date, selectedData):

    if selectedData == 'raw':
        df = fetch_raw_dataframe(uid, date)
        total = df['pop'].sum()
        df['text'] = 'Occurrence ' + df['pop'].astype(str) + ' / ' + str(total)
        scale = 15
        scale_2 = 8
        zoom=12.2
        data = Data([
            Scattermapbox(
                lat=df['lat'],
                lon=df['lon'],
                text=df['text'],
                mode='markers',
                marker=dict(
                        size=df['pop']*scale,
                        sizemode = 'area',
                        color='orangered'
                    ),
                hoverinfo = "lon+lat+text",
                name = "Cellular Base Stations",
            ),
        ])
        layout['showlegend'] = True
        layout['mapbox']['center']['lon'] = df['lon'].astype(float).mean()
        layout['mapbox']['center']['lat'] = df['lat'].astype(float).mean()

    elif selectedData == 'prepro':
        df = fetch_prepro_dataframe(uid, date)
        endpt_size=20
        zoom=12.2
        scale=30
        data = Data([
            Scattermapbox(
                lat=[df.lat.loc[i] for i in df.index],
                lon=[df.lon.loc[i] for i in df.index],
                text=[df.start_t.loc[i]+' - '+df.end_t.loc[i]+'<br>Stayed '+df.stay_t.loc[i]+'s' for i in df.index],
                mode='markers+lines',
                marker=Marker(
                    #color="royalblue",
                    color=np.log(df.stay_t.astype(int)),
                    autocolorscale=True,
                    #size=np.log(df.stay_t.astype(int))*scale,
                    #sizemode='area',
                    size=15,
                ),
                hoverinfo = "lon+lat+text",
                name = "Cellular Trajectory"
            )
        ])
        layout['showlegend'] = True
        layout['mapbox']['center']['lon'] = np.mean([float(df.lon.loc[i]) for i in df.index])
        layout['mapbox']['center']['lat'] = np.mean([float(df.lat.loc[i]) for i in df.index])

    elif selectedData == 'mode':
        user_df, route_df, user_ddf = fetch_mode_dataframe(uid, date)
        endpt_size=20
        zoom=12.2
        data = Data([
            Scattermapbox(
                lat=[user_df.lat.loc[i] for i in user_df.index],
                lon=[user_df.lon.loc[i] for i in user_df.index],
                mode='markers+lines',
                marker=Marker(
                    color="silver",
                    size=4,
                    opacity=0.5
                ),
                name = "Cellular Trajectory",
                hoverinfo = "skip",
            ),
            Scattermapbox(
                lat=[route_df.lat.loc[i] for i in route_df.index],
                lon=[route_df.lon.loc[i] for i in route_df.index],
                text=[route_df.route_name.loc[i]+'<br>'+route_df.order.loc[i]+'/'+route_df.stop_name.loc[i] for i in route_df.index],
                mode='markers+lines',
                marker=Marker(
                    size=[endpt_size] + [4 for j in range(len(route_df.index) - 2)] + [endpt_size],
                    color="rgb(0,116,217)"
                ),
                name = "Bus Route",
                hoverinfo = "text",
            ),
            Scattermapbox(
                lat=[user_ddf.lat.loc[i] for i in user_ddf.index],
                lon=[user_ddf.lon.loc[i] for i in user_ddf.index],
                text=[user_ddf.start_t.loc[i]+' - '+user_ddf.end_t.loc[i]+'<br>Stayed '+user_ddf.stay_t.loc[i]+'s' for i in user_ddf.index],
                mode='markers+lines',
                marker=Marker(
                    color="rgb(255,65,54)",
                    size=[endpt_size] + [4 for j in range(len(user_ddf.index) - 2)] + [endpt_size]
                ),
                name = "Detected Trajectory",
                hoverinfo = "lon+lat+text",
            )
        ])
        layout['showlegend'] = True
        layout['mapbox']['center']['lon'] = np.mean([float(user_df.lon.loc[i]) for i in user_df.index])
        layout['mapbox']['center']['lat'] = np.mean([float(user_df.lat.loc[i]) for i in user_df.index])

    fig = dict(data=data, layout=layout)
    return fig


@app.server.before_first_request
def defineTotalList():
    global raw_df, prepro_df, route_df, user_ddf
    raw_df, prepro_df, route_df, user_ddf = initialize()


if __name__ == '__main__':
    app.run_server(debug=True)
