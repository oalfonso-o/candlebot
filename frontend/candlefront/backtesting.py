import logging
import requests
import datetime
import itertools
from collections import defaultdict, OrderedDict

import flask
from flask import Blueprint, render_template

from candlefront import config
from candlebot import utils
from candlefront.routes import ROUTES

logger = logging.getLogger(__name__)


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

backtesting_bp = Blueprint('backtesting', __name__)


@backtesting_bp.route('/backtesting')
def backtesting():
    backtests_response = requests.get(
        '/'.join([config.API, 'backtesting', 'list']))
    backtests_to_table = get_backtests(backtests_response)
    symbols = requests.get('/'.join([config.API, 'forms', 'symbols']))
    intervals = requests.get('/'.join([config.API, 'forms', 'intervals']))
    strategies = requests.get(
        '/'.join([config.API, 'backtesting', 'strategies']))
    strategies_json = strategies.json()
    form_args = get_form_args(strategies_json)
    return render_template(
        'backtesting.html',
        symbol_options=symbols.json(),
        interval_options=intervals.json(),
        routes=ROUTES,
        submit_button_text='Backtest',
        submit_endpoint='/backtesting',
        show_strategy=True,
        backtests=backtests_to_table,
        backtesting_header_map=backtesting_header_map,
        strategies=strategies_json,
        args=form_args,
    )


def get_backtests(backtests_response):
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
    return backtests_to_table


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


def get_form_args(strategies):
    args = dict(flask.request.args)
    date_from = datetime.date(year=2000, month=1, day=1)
    args['date_from'] = args.get('date_from') or date_from
    date_to = datetime.date.today()
    args['date_to'] = args.get('date_to') or date_to
    first_strat = list(strategies.keys())[0]
    args['strategy'] = args.get('strategy') or first_strat
    return args
