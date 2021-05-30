import json
import logging
import requests
import datetime

import flask
from flask import render_template, Blueprint

from candlefront import config
from candlefront.routes import ROUTES

logger = logging.getLogger(__name__)

charts_bp = Blueprint('charts', __name__)


@charts_bp.route('/', methods=['GET', 'POST'])
def charts():
    symbol_selected = 'ADAUSDT'
    interval_selected = '1h'
    strategy_selected = 'triangle'
    date_from = datetime.date.today() - datetime.timedelta(days=230)
    date_to = datetime.date.today() + datetime.timedelta(days=1)
    strategy_params = {
        'date_from': date_from,
        'date_to': date_to,
        'symbol': symbol_selected,
        'interval': interval_selected,
    }
    if flask.request.method == 'POST':
        strategy_params = {
            'date_from': flask.request.form['date_from'],
            'date_to': flask.request.form['date_to'],
            'symbol': flask.request.form['symbol'],
            'interval': flask.request.form['interval'],
        }
        symbol_selected = strategy_params['symbol']
        interval_selected = strategy_params['interval']
        date_from = strategy_params['date_from']
        date_to = strategy_params['date_to']
        strategy_selected = flask.request.form['strategy']
    symbols = requests.get('/'.join([config.API, 'forms', 'symbols']))
    intervals = requests.get('/'.join([config.API, 'forms', 'intervals']))
    data_points_response = requests.get(
        '/'.join([config.API, 'strategies', strategy_selected]),
        params=strategy_params,
    )
    strategies = requests.get(
        '/'.join([config.API, 'backtesting', 'strategies']))
    if data_points_response.status_code != 200:
        logger.error(data_points_response.json())
        data_points_response.raise_for_status()
    strategy_params['strategy'] = strategy_selected
    return render_template(
        'index.html',
        symbol_options=symbols.json(),
        symbol_selected=symbol_selected,
        interval_selected=interval_selected,
        strategy_selected=strategy_selected,
        interval_options=intervals.json(),
        strategy_options=strategies.json(),
        data_points=json.dumps(data_points_response.json()),
        show_strategy=True,
        submit_button_text='Charts',
        submit_endpoint='/',
        date_from=date_from,
        date_to=date_to,
        strategy_params=strategy_params,
        routes=ROUTES,
    )
