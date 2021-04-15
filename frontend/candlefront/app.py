import os
import requests
import json
from dotenv import load_dotenv

import flask
from flask import Flask
from flask import render_template
from flask import send_from_directory

load_dotenv(override=True)

API = os.getenv('CANDLEFRONT_API_ENDPOINT')

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates',
)


@app.route('/', methods=['GET', 'POST'])
def get_charts():
    if (flask.request.form):
        selected_symbol = flask.request.form['symbol']
        selected_interval = flask.request.form['interval']
        print(selected_symbol, selected_interval)
        # TODO: use form values for data_points request
    symbols = requests.get('/'.join([API, 'forms', 'symbols']))
    intervals = requests.get('/'.join([API, 'forms', 'intervals']))
    data_points = requests.get('/'.join([API, 'strategies', 'ema']))
    return render_template(
        'index.html',
        symbol_options=symbols.json(),
        interval_options=intervals.json(),
        data_points=json.dumps(data_points.json()),
    )


@app.route('/backfill')
def backfill():
    symbols = requests.get('/'.join([API, 'forms', 'symbols']))
    intervals = requests.get('/'.join([API, 'forms', 'intervals']))
    return render_template(
        'backfill.html',
        symbol_options=symbols,
        interval_options=intervals,
    )


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )
