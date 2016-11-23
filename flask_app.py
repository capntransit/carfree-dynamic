
# A very simple Flask Hello World app for you to get started with...
import json
import os
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

CONFIG = {}

API_URL = 'http://api.census.gov/data/2014/acs5?get=NAME,B08141_{var}&for={forc}&in={inc}&key={key}'

DEFAULT_FOR = 'tract:*'
DEFAULT_IN = 'state:36 county:81'

LOCAL_DIR = os.path.dirname(__file__)

VARS = {
    '001E': 'Total',
    '001M': 'Margin Of Error For Total',
    '002E': 'No vehicle available',
    '002M': 'Margin Of Error For No vehicle available'
    }

with open('/'.join([LOCAL_DIR, 'config.json'])) as configdata:
    CONFIG = json.load(configdata)

@app.route('/', methods=['GET', 'POST'])
def census():

    cols = {}
    locs = []

    param = {
        'vars': VARS
        }

    forc = request.values.get('for', DEFAULT_FOR)
    inc = request.values.get('in', DEFAULT_IN)

    for var, name in VARS.items():
        res = requests.get(
            API_URL.format(var=var, inc=inc, forc=forc, key=CONFIG['CENSUS_KEY'])
            ).json()
        res.pop(0)
        for idx, loc in enumerate(res):
            if var == '001E':
                locs.append(loc[0])
            if loc[0] not in cols:
                cols[loc[0]] = {}
            cols[loc[0]][var] = loc[1]
            cols[loc[0]]['Tract'] = loc[4]

    for loc in locs:
        cols[loc]['Ratio'] = 0
        if int(cols[loc]['001E']) > 0:
            cols[loc]['Ratio'] = str(
                round(int(cols[loc]['002E']) / int(cols[loc]['001E']), 3)
                )

    param['in'] = inc
    param['for'] = forc
    param['cols'] = cols
    return render_template('getdata.html', param=param)

