
# A very simple Flask Hello World app for you to get started with...
import json
import os
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

CONFIG = {}

API_URL = 'http://api.census.gov/data/2014/acs5?get=NAME,B08141_{var}&for={geo}&key={key}'

DEFAULT_GEO = 'region:*'
DEFAULT_VAR = '001E'

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

    geo = request.values.get('geo', DEFAULT_GEO)

    for var, name in VARS.items():
        res = requests.get(
            API_URL.format(var=var, geo=geo, key=CONFIG['CENSUS_KEY'])
            ).json()
        res.pop(0)
        for idx, loc in enumerate(res):
            if var == '001E':
                locs.append(loc[0])
            if loc[0] not in cols:
                cols[loc[0]] = {}
            cols[loc[0]][var] = loc[1]

    for loc in locs:
        cols[loc]['Ratio'] = str(
            round(int(cols[loc]['002E']) / int(cols[loc]['001E']), 3)
            )

    param['geo'] = geo
    param['cols'] = cols
    return render_template('getdata.html', param=param)

