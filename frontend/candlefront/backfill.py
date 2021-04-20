import json
import logging
import requests
import datetime

import flask
from flask import render_template, Blueprint

from candlefront import config
from candlefront.routes import ROUTES

logger = logging.getLogger(__name__)

backfill_bp = Blueprint('backfill', __name__)


@backfill_bp.route('/backfill', methods=['GET', 'POST'])
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
            '/'.join([config.API, 'backfill', 'create']),
            data=json.dumps(data),
        )
        if response.status_code != 200:
            logger.error(response.json())
            response.raise_for_status()
    backfill = requests.get('/'.join([config.API, 'backfill', 'list']))
    symbols = requests.get('/'.join([config.API, 'forms', 'symbols', 'all']))
    intervals = requests.get(
        '/'.join([config.API, 'forms', 'intervals', 'all']))
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
