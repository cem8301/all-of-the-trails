#!/usr/bin/env python3
from flask import Flask
import requests
import pandas as pd
# from pandas.tseries.offsets import *
from flatten_dict import flatten
from stravalib import Client
import polyline
import os
import json
import datetime
import urllib.parse
import dash
import dash_leaflet as dl
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dotenv import load_dotenv
from threading import Thread

load_dotenv()
server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server
)
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    html.A("Get Some Data!", href=(
           "https://www.strava.com/oauth/authorize?client_id=32737"
           "&response_type=code&redirect_uri=https://www.giraffesinaboat.com"
           "/exchange_token&approval_prompt=force&scope=activity:read_all"))])

local_timezone = datetime.datetime.now(datetime.timezone(datetime.timedelta(0))).astimezone().tzinfo
dend = pd.Timestamp.today() + pd.DateOffset(years=1)
datelist = pd.date_range(start='1/1/2009', end=dend, freq='Y', tz=local_timezone)
maxmarks = len(datelist) - 1
DLIST = pd.DatetimeIndex(datelist).normalize()
TAGS = {}
for idx, item in enumerate(DLIST):
    TAGS[idx] = (item + pd.DateOffset(months=1)).strftime('%Y')

page_1_layout = html.Div([
    dcc.Loading(
        id="loading-1",
        type="default",
        fullscreen=True,
        children=[html.Div(dcc.Store(id='memory')),
                  html.Div(dcc.Store(id='local', storage_type='local')),
                  html.Div(dcc.Store(id='session', storage_type='session')),
                  html.Div(dcc.Dropdown(
                           id='dropdown',
                           multi=True,
                           placeholder="Select Activity Type")),
                  html.Div(dcc.Dropdown(
                           id='dropdown2',
                           multi=True,
                           placeholder="Select Gear")),
                  html.Div(dcc.RangeSlider(
                           id='time-slider',
                           updatemode='mouseup',
                           count=1,
                           min=0,
                           max=maxmarks,
                           step=1,
                           value=[0, maxmarks],
                           marks=TAGS,
                           pushable=1))]
    ),
    html.Div(id='test',
             style={'width': '100%',
                    'height': '600px',
                    'margin': 'auto',
                    'display': 'block'})
])

@server.route('/hello')
def hello():
    return 'hello world!'

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('url', 'href')]
)
def display_page(pathname, href):
    if pathname == '/exchange_token':
        return page_1_layout
    else:
        return index_page

@app.callback(
    Output('memory', 'data'),
    [Input('url', 'href')],
    State('memory', 'data')
)
def get_user_data(href, data):
    parsed_url = urllib.parse.urlparse(href)
    parsed_query = urllib.parse.parse_qs(parsed_url.query)
    code = parsed_query['code'][0]
    sd = StravaData(code)
    df = sd.get_data()
    activity_types = sd.get_activity_types()
    gear_list = sd.get_gear_ids()
    all_data = {'df': df,
                'activity_types': activity_types,
                'gear_list': gear_list}
    return json.dumps(all_data)

@app.callback(
    Output('dropdown', 'options'),
    Input('memory', 'modified_timestamp'),
    State('memory', 'data')
)
def set_dropdown(ts, data):
    if ts is None:
        raise PreventUpdate
    activity_types = json.loads(data)['activity_types']
    return activity_types

@app.callback(
    Output('dropdown2', 'options'),
    [Input('memory', 'modified_timestamp'),
        Input('dropdown', 'value')],
    State('memory', 'data')
)
def set_dropdown2(ts, idx_list1, data):
    if ts is None:
        raise PreventUpdate
    if idx_list1 is None:
        return {}
    df = pd.DataFrame.from_dict(json.loads(data)['df'])
    activity_types = json.loads(data)['activity_types']
    gear_list = json.loads(data)['gear_list']
    subset_gear_list = get_relavent_gear(idx_list1, df, activity_types, gear_list)
    return subset_gear_list

@app.callback(
    Output('time-slider', 'min'),
    Input('memory', 'modified_timestamp'),
    State('memory', 'data')
)
def set_dropdown3(ts, data):
    if ts is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(json.loads(data)['df'])
    first = pd.to_datetime(df['start_date_local'][-1])
    pos = DLIST.get_loc(first, method='nearest') - 1
    return pos

@app.callback(
    Output('test', 'children'),
    [Input('dropdown', 'value'),
        Input('dropdown2', 'value'),
        Input('time-slider', 'value'),
        Input('memory', 'modified_timestamp')],
    State('memory', 'data')
)
def set_map(idx_list1, idx_list2, slider, ts, data):
    if ts is None:
        raise PreventUpdate
    if idx_list1 is None:
        return ""
    df = pd.DataFrame.from_dict(json.loads(data)['df'])
    # Limit by slider date
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    df = df[df['start_date_local'] > DLIST[slider[0]]]
    df = df[df['start_date_local'] < DLIST[slider[1]]]
    # Limit by activity and gear selection
    activity_types = json.loads(data)['activity_types']
    gear_list = json.loads(data)['gear_list']
    data, latlng = get_polylines(df,
                                 activity_types,
                                 idx_list1,
                                 gear_list,
                                 idx_list2)
    patterns = [dict(offset='100%', repeat='0')]
    marker_pattern = dl.PolylineDecorator(children=data,
                                          patterns=patterns)
    return dl.Map([dl.TileLayer(), marker_pattern],
                  id='map',
                  center=(latlng[0][0], latlng[0][1]))

def get_relavent_gear(idx_list1, df, activity_types, gear_list):
    df = df.dropna()
    mid = []
    for idx in idx_list1:
        mid.append(activity_types[idx]['label'])
    df_sub = df[df['type'].isin(mid)]
    grouped = df_sub.groupby('type')['gear_id'].apply(lambda x: list(set(x))).to_list()
    options = sum(grouped, [])
    subset_gear_list = []
    for gear_id in gear_list:
        if gear_id['value'] in options:
            subset_gear_list.append(gear_id)
    return subset_gear_list

def get_polylines(df, activity_types, idx_list1, gear_list, idx_list2):
    if idx_list1 != []:
        # Grab data by gear_id or type
        subset_gear_list = get_relavent_gear(idx_list1, df, activity_types, gear_list)
        if idx_list1 != [0]:
            mid = []
            for idx in idx_list1:
                mid.append(activity_types[idx]['label'])
            df = df[df['type'].isin(mid)]
        if idx_list2 != [] and idx_list2 is not None:
            for item in subset_gear_list:
                if item['value'] not in idx_list2:
                    df = df[df['gear_id'] != item['value']]
    polylines = df['map/summary_polyline'].dropna().values.tolist()
    lines = []
    for item in polylines:
        lines.append(polyline.decode(item))
    data = dl.Polyline(positions=lines)
    latlng = lines[0]
    return data, latlng

class Threader(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self._return = None

    def run(self):
        if self.target is not None:
            self._return = self.target(*self.args,
                                       **self.kwargs)

    def join(self):
        Thread.join(self)
        return self._return

class StravaData:
    def __init__(self, code):
        self.headers = self.get_headers(code)
        self.col_names = ['map/summary_polyline',
                          'start_date_local',
                          'type',
                          'name',
                          'gear_id']
        self.df = pd.DataFrame(columns=self.col_names)

    def get_headers(self, code):
        STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
        STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
        client = Client()
        access_dict = client.exchange_code_for_token(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code=code)
        token = access_dict["access_token"]
        headers = {'Authorization': "Bearer {0}".format(token)}
        return headers

    def get_activity_types(self):
        types = self.df.type.unique().tolist()
        activity_types = [{'label': 'All',
                           'value': 0}]
        for idx, each_type in enumerate(types):
            activity_types.append({'label': each_type,
                                   'value': idx + 1})
        return activity_types

    def get_data(self):
        threads = list()
        page = 1
        num_threads = 6
        ans = True
        while ans:
            for index in range(page, page + num_threads):
                x = Threader(target=self.run_query, args=(index,))
                threads.append(x)
                x.start()
            for index, thread in enumerate(threads):
                ans = thread.join()
            if not ans:
                break
            page += num_threads
            if page > 300:
                print('Page count is over 300 something may be wrong')
                ans = False
                break
        return self.df.to_dict()

    def run_query(self, page):
        data = True
        response = requests.get(f"https://www.strava.com/api/v3/"
                                f"athlete/activities?page={page}",
                                headers=self.headers).json()
        for r in response:
            r.pop('start_latlng', None)
            r.pop('end_latlng', None)
            df_tmp = pd.DataFrame(flatten(r, reducer='path'), index=[0])
            df_tmp = df_tmp[self.col_names]
            self.df = self.df.append(df_tmp, ignore_index=True)
        print(f"Page {page} has {len(response)} data points")
        if len(response) == 0:
            print(f"Finished gathering data for page: {page}")
            data = False
        return data

    def get_gear_ids(self):
        gear_ids = self.df.gear_id.unique().tolist()
        gear_list = []
        for idx, gear_id in enumerate(gear_ids):
            if gear_id is not None:
                gear_names = requests.get(
                    f"https://www.strava.com/api/v3/gear/{gear_id}",
                    headers=self.headers).json()
                gear_list.append({'label': gear_names['name'],
                                  'value': gear_id})
        return gear_list


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0')
