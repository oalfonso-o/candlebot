import logging
import requests
import datetime
import itertools
from collections import defaultdict, OrderedDict

import flask
from flask import Blueprint, render_template

from candlebot import constants as apiconstants

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
    if flask.request.args.get('create_test_checkbox'):
        create_backtest()
    symbols = requests.get('/'.join([config.API, 'forms', 'symbols', 'all']))
    intervals = requests.get('/'.join([config.API, 'forms', 'intervals']))
    strategies = requests.get(
        '/'.join([config.API, 'backtesting', 'strategies']))
    strategies_json = strategies.json()
    form_args = get_form_args(strategies_json)
    backtest_list_params = {
        'strategy': form_args['strategy'],
        'symbols': [],
        'intervals': [],
        'date_from': form_args['date_from'],
        'date_to': form_args['date_to'],
    }
    for arg in form_args:
        if arg.startswith('interval'):
            backtest_list_params['intervals'].append(arg.split('_')[1])
        if arg.startswith('symbol'):
            backtest_list_params['symbols'].append(arg.split('_')[1])
    backtest_list_params['symbols'] = ','.join(backtest_list_params['symbols'])
    backtest_list_params['intervals'] = ','.join(
        backtest_list_params['intervals'])
    backtests_response = requests.get(
        '/'.join([config.API, 'backtesting', 'list']),
        params=backtest_list_params,
    )
    backtests_json_response = backtests_response.json()
    last_backtests = get_backtests(backtests_json_response['last_backtests'])
    best_backtests = get_backtests(backtests_json_response['best_backtests'])
    filtered_backtests = get_backtests(
        backtests_json_response['filtered_backtests'])
    all_backtests = {
        'last_backtests': last_backtests,
        'best_backtests': best_backtests,
        'filtered_backtests': filtered_backtests,
    }
    return render_template(
        'backtesting.html',
        symbol_options=symbols.json(),
        interval_options=intervals.json(),
        routes=ROUTES,
        submit_button_text='Backtest',
        submit_endpoint='/backtesting',
        show_strategy=True,
        all_backtests=all_backtests,
        backtesting_header_map=backtesting_header_map,
        strategies=strategies_json,
        args=form_args,
    )


def create_backtest():
    form_args = dict(flask.request.args)
    symbols = []
    intervals = []
    strategy_fields = []
    indicators_fields = []
    strat_var_prefix = (
        apiconstants.BACKTESTING_STRAT_PREFIX
        + apiconstants.BACKTESTING_STRAT_IND_SEPARATOR
    )
    ind_var_prefix = (
        apiconstants.BACKTESTING_IND_PREFIX
        + apiconstants.BACKTESTING_STRAT_IND_SEPARATOR
    )
    for arg_key, arg_value in form_args.items():
        if arg_key.startswith('symbol'):
            symbol = arg_key.split('_')[-1]
            symbols.append(symbol)
        elif arg_key.startswith('interval'):
            interval = arg_key.split('_')[-1]
            intervals.append(interval)
        elif arg_key.startswith(strat_var_prefix):
            strategy_fields.append({'key': arg_key, 'value': arg_value})
        elif arg_key.startswith(ind_var_prefix):
            indicators_fields.append({'key': arg_key, 'value': arg_value})
    args = {
        'date_from': form_args['date_from'],
        'date_to': form_args['date_to'],
        'strategy': form_args['strategy'],
        'symbols': symbols,
        'intervals': intervals,
        'strategy_fields': strategy_fields,
        'indicators_fields': indicators_fields,
    }
    create_backtest_response = requests.post(
        '/'.join([config.API, 'backtesting', 'create']),
        json=args,
    )
    if create_backtest_response.status_code == 422:
        logger.error(create_backtest_response.json())
    create_backtest_response.raise_for_status()


def get_backtests(response_backtests):
    backtests_to_table = defaultdict(dict)
    backtests = itertools.groupby(
        response_backtests,
        key=lambda r: r['strategy']
    )
    for strategy, rows in backtests:
        rows_list = list(rows)
        header_keys = list(backtesting_header_map.keys())
        header_values = list(backtesting_header_map.values())
        header_specific_fields = []
        for key in rows_list[0].keys():
            if key not in header_keys:
                header_specific_fields.append(
                    {'mongo_key': key, 'output_key': key.split('-')[-1]})
        specific_header_values = sorted(
            [k['output_key'] for k in header_specific_fields])
        header_values += specific_header_values
        specific_header_keys = sorted(
            [k['mongo_key'] for k in header_specific_fields])
        header_keys += specific_header_keys
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
    args.pop('create_test_checkbox', None)
    return args
