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
    strategy_params = {
        'date_from': datetime.date(year=2000, month=1, day=1),
        'date_to': datetime.date.today(),
        'symbol': 'ADAUSDT',
        'interval': '1d',
    }
    if flask.request.method == 'POST':
        strategy_params = {
            'date_from': flask.request.form['date_from'],
            'date_to': flask.request.form['date_to'],
            'symbol': flask.request.form['symbol'],
            'interval': flask.request.form['interval'],
        }
    symbols = requests.get('/'.join([config.API, 'forms', 'symbols']))
    intervals = requests.get('/'.join([config.API, 'forms', 'intervals']))
    data_points_response = requests.get(
        '/'.join([config.API, 'strategies', 'ema']),
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
