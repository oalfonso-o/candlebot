import logging
import os
import requests
import json
import datetime
from dotenv import load_dotenv

import flask
from flask import Flask
from flask import render_template
from flask import send_from_directory

from candlebot import constants as apiconstants
from candlefront.routes import ROUTES

logging.basicConfig(
    level=logging.INFO,
    format=(
        '%(asctime)s %(name)16.16s %(funcName)10.10s %(levelname)7s: '
        '%(message)s'
    ),
    force=True,
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

API = os.getenv('CANDLEFRONT_API_ENDPOINT')

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates',
)


@app.route('/', methods=['GET', 'POST'])
def charts():
    strategy_params = {
        'date_from': datetime.date(year=2000, month=1, day=1),
        'date_to': datetime.date.today(),
        'symbol': apiconstants.SYMBOL_BITCOIN_EURO,
        'interval': '1d',
    }
    if flask.request.method == 'POST':
        strategy_params = {
            'date_from': flask.request.form['date_from'],
            'date_to': flask.request.form['date_to'],
            'symbol': flask.request.form['symbol'],
            'interval': flask.request.form['interval'],
        }
    symbols = requests.get('/'.join([API, 'forms', 'symbols']))
    intervals = requests.get('/'.join([API, 'forms', 'intervals']))
    data_points_response = requests.get(
        '/'.join([API, 'strategies', 'ema']),
        params=strategy_params,
    )
    if data_points_response.status_code != 200:
        logger.error(data_points_response.json())
        data_points_response.raise_for_status()
    strategy_params['strategy'] = 'ema'
    return render_template(
        'index.html',
        symbol_options=symbols.json(),
        interval_options=intervals.json(),
        data_points=json.dumps(data_points_response.json()),
        show_strategy=True,
        submit_button_text='Charts',
        submit_endpoint='/',
        date_from=datetime.date(year=2000, month=1, day=1),
        date_to=datetime.date.today(),
        strategy_params=strategy_params,
        routes=ROUTES,
    )


@app.route('/backfill', methods=['GET', 'POST'])
def backfill():
    response = None
    if flask.request.method == 'POST':
        data = {
            'date_from': flask.request.form['date_from'],
            'date_to': flask.request.form['date_to'],
            'symbol': flask.request.form['symbol'],
            'interval': flask.request.form['interval'],
        }
        response = requests.post(
            '/'.join([API, 'backfill', 'create']),
            data=json.dumps(data),
        )
        if response.status_code != 200:
            logger.error(response.json())
            response.raise_for_status()
    backfill = requests.get('/'.join([API, 'backfill', 'list']))
    symbols = requests.get('/'.join([API, 'forms', 'symbols', 'all']))
    intervals = requests.get('/'.join([API, 'forms', 'intervals', 'all']))
    return render_template(
        'backfill.html',
        symbol_options=symbols.json(),
        interval_options=intervals.json(),
        show_strategy=False,
        submit_button_text='Backfill',
        date_from=datetime.date(year=2000, month=1, day=1),
        date_to=datetime.date.today(),
        submit_endpoint='/backfill',
        form_response=response.text if response else '',
        routes=ROUTES,
        backfill=backfill.json(),
    )


@app.route('/backtesting', methods=['GET', 'POST'])
def backtesting():
    symbols = requests.get('/'.join([API, 'forms', 'symbols']))
    intervals = requests.get('/'.join([API, 'forms', 'intervals']))
    return render_template(
        'backtesting.html',
        symbol_options=symbols.json(),
        interval_options=intervals.json(),
        date_from=datetime.date(year=2000, month=1, day=1),
        date_to=datetime.date.today(),
        routes=ROUTES,
        submit_button_text='Backtest',
        submit_endpoint='/backtesting',
        show_strategy=True,
    )


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )