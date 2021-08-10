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
    symbol_selected = 'BNBUSDT'
    interval_selected = '15m'
    strategy_selected = 'scalping_yolo'
    date_from = datetime.date.today() - datetime.timedelta(days=40)
    date_to = datetime.date.today() + datetime.timedelta(days=1)
    strategy_params = {
        'date_from': date_from,
        'date_to': date_to,
        'symbol': symbol_selected,
        'interval': interval_selected,
        'strategy': strategy_selected,
    }
    if flask.request.method == 'POST':
        strategy_params = {
            'date_from': flask.request.form['date_from'],
            'date_to': flask.request.form['date_to'],
            'symbol': flask.request.form['symbol'],
            'interval': flask.request.form['interval'],
            'strategy': flask.request.form['strategy'],
        }
        symbol_selected = strategy_params['symbol']
        interval_selected = strategy_params['interval']
        date_from = strategy_params['date_from']
        date_to = strategy_params['date_to']
        strategy_selected = strategy_params['strategy']

    symbols = requests.get('/'.join([config.API, 'forms', 'symbols']))
    intervals = requests.get('/'.join([config.API, 'forms', 'intervals']))
    strat_response = get_strat_response(strategy_params=strategy_params)
    legend = get_legend(strat_response)
    strategies = requests.get(
        '/'.join([config.API, 'backtesting', 'strategies']))
    strategies = strategies.json()
    strategy_params['strategy'] = strategy_selected
    return render_template(
        'index.html',
        symbol_options=symbols.json(),
        symbol_selected=symbol_selected,
        interval_selected=interval_selected,
        strategy_selected=strategy_selected,
        interval_options=intervals.json(),
        strategy_options=strategies,
        data_points=json.dumps(strat_response['charts']),
        legend=legend,
        show_strategy=True,
        submit_button_text='Charts',
        submit_endpoint='/',
        date_from=date_from,
        date_to=date_to,
        strategy_params=strategy_params,
        routes=ROUTES,
    )


def get_strat_response(strategy_params):
    data_points_response = requests.get(
        '/'.join([config.API, 'strategies']),
        params=strategy_params,
    )
    if data_points_response.status_code != 200:
        logger.error(data_points_response.json())
        data_points_response.raise_for_status()
    data_points = data_points_response.json()
    return data_points


def get_legend(strat_response):
    lines_indicators = {
        serie['title']: serie['color']
        for data in strat_response['charts']
        for serie in data['series']
        if serie['type'] != 'candles'
    }
    return {
        'stats': strat_response['stats'],
        'lines_indicators': lines_indicators,
        'markers_indicators': strat_response['markers'],
    }
