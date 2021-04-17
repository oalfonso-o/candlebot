import os
import json
import logging
import requests
import datetime
import itertools
from collections import defaultdict, OrderedDict
from dotenv import load_dotenv

import flask
from flask import Flask
from flask import render_template
from flask import send_from_directory

from candlebot import constants as apiconstants
from candlebot import utils
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

backtesting_header_map = OrderedDict({
    'strategy': 'st',
    'symbol': 'sy',
    'interval': 'i',
    'profit_percentage': '+%',
    'balance_origin_start': 'bos',
    'balance_origin_end': 'boe',
    'amount_to_open': 'o',
    'balance_long': 'bl',
    'open_positions_long': 'opl',
    'close_positions_long': 'cpl',
    'total_earned_long': 'tel',
    'balance_short': 'bs',
    'open_positions_short': 'ops',
    'close_positions_short': 'cps',
    'total_earned_short': 'tes',
    'df': 'df',
    'dt': 'dt',
    'test_date': 'd',
    'test_id': 'id',
})


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
    if flask.request.method == 'POST':
        # TODO: request to API
        pass
    backtests_response = requests.get('/'.join([API, 'backtesting', 'list']))
    # key: strategy, value: dict with "tests" and "header"
    backtests_to_table = defaultdict(dict)
    backtests = itertools.groupby(
        backtests_response.json(),
        key=lambda r: r['strategy']
    )
    for strategy, rows in backtests:
        rows_list = list(rows)
        header_keys = backtesting_header_map.keys()
        header_values = list(backtesting_header_map.values())
        for key in rows_list[0].keys():
            if key not in header_keys:
                header_values.append(key.split('-')[-1])
        tests = [sort_row_with_header(row, header_keys) for row in rows_list]
        header = itertools.zip_longest(header_values, header_keys)
        backtests_to_table[strategy]['tests'] = tests
        backtests_to_table[strategy]['header'] = header
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
        backtests=backtests_to_table,
        backtesting_header_map=backtesting_header_map,
    )


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )


def sort_row_with_header(row, header):
    parsed_row = []
    for h in header:
        v = row[h]
        if isinstance(v, float):
            v = round(v, 4)
        if h == 'test_date':
            v = utils.str_datetime_to_datetime(v).date()
        parsed_row.append(v)
    for row_key in row:
        if row_key not in header:
            parsed_row.append(row[row_key])
    return parsed_row
