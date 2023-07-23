import csv
import logging
import datetime
import itertools
from collections import defaultdict

import numpy as np

from candlebot import utils
from candlebot import constants
from candlebot.settings import Settings
from candlebot.db import db_insert
from candlebot.strategist import Strategist
from candlebot.db.candle_retriever import CandleRetriever

logger = logging.getLogger(__name__)


class Backtesting:
    generic_header = [
        'test_id',
        'strategy',
        'symbol',
        'interval',
        'df',
        'dt',
        'test_date',
    ]
    wallet_header = [
        'profit_percentage',
        'balance_origin_start',
        'balance_origin_end',
        'amount_to_open',
        'balance_long',
        'open_positions_long',
        'close_positions_long',
        'fees_payed',
    ]
    range_sufixes = ['_from', '_to', '_step']

    def __init__(self):
        self.test_date = datetime.datetime.utcnow()
        self.output_rows = []
        self.sep = constants.BACKTESTING_STRAT_IND_SEPARATOR
        self.strat_prefix = constants.BACKTESTING_STRAT_PREFIX
        self.ind_prefix = constants.BACKTESTING_IND_PREFIX

    def test_from_web(self, args):
        strategy = args.strategy
        date_from_without_dash = args.date_from.replace('-', '')
        date_to_without_dash = args.date_to.replace('-', '')
        Settings.BT['output']['csv']['active'] = False
        Settings.BT['output']['mongo']['active'] = True
        Settings.BT['dates'] = [
            {'df': date_from_without_dash, 'dt': date_to_without_dash}
        ]
        header = []

        override_strategies = {strategy: {}}
        strategies_ranges_dict = defaultdict(dict)
        for f in args.strategy_fields:
            key = f['key'].split(self.sep)[-1]
            if not any([s in key for s in self.range_sufixes]):
                header.append(f['key'])
                value = True if f['value'] == 'true' else f['value']
                override_strategies[strategy][key] = [value]
            else:
                suffix = key.split('_')[-1]
                key = '_'.join(key.split('_')[:-1])
                strategies_ranges_dict[key][suffix] = f['value']

        override_indicators = defaultdict(dict)
        override_indicators.update(Settings.BT['indicators'])
        for ind, values in override_indicators.items():
            for val_key, val in values.items():
                override_indicators[ind][val_key] = [val]
        indicators_ranges_dict = defaultdict(lambda: defaultdict(dict))
        for f in args.indicators_fields:
            key_parts = f['key'].split(self.sep)
            key = key_parts[-1]
            ind = key_parts[1]
            if not any([s in key for s in self.range_sufixes]):
                header.append(f['key'])
                value = True if f['value'] == 'true' else f['value']
                override_indicators[ind][key] = [value]
            else:
                suffix = key.split('_')[-1]
                key = '_'.join(key.split('_')[:-1])
                indicators_ranges_dict[ind][key][suffix] = f['value']

        ranges_strategies = defaultdict(dict)
        for key, v in strategies_ranges_dict.items():
            header_key = self.sep.join([
                constants.BACKTESTING_STRAT_PREFIX,
                strategy,
                key,
            ])
            header.append(header_key)
            ranges_strategies[strategy][key] = [
                float(v['from']),
                float(v['to']),
                float(v['step']),
            ]

        ranges_indicators = defaultdict(dict)
        for ind, ranges in indicators_ranges_dict.items():
            for key, v in ranges.items():
                header_key = self.sep.join([
                    constants.BACKTESTING_IND_PREFIX,
                    ind,
                    key,
                ])
                header.append(header_key)
                ranges_indicators[ind][key] = [
                    float(v['from']),
                    float(v['to']),
                    float(v['step']),
                ]

        test_id = f'{strategy}_web'
        test_config = {}
        Settings.BT['tests'][test_id] = test_config
        test_config['strategy'] = strategy
        test_config['header'] = header
        test_config['override'] = {
            'intervals': args.intervals,
            'symbols': args.symbols,
            'strategies': override_strategies,
            'indicators': override_indicators,
        }
        test_config['ranges'] = {
            'strategies': ranges_strategies,
            'indicators': ranges_indicators,
        }
        self.test(test_id)

    def test(self, test_id):
        self.test_id = test_id
        self.bt_config = self._config(test_id)
        self._set_header()
        generic_fields = [
            self.bt_config['symbols'],
            self.bt_config['intervals'],
            self.bt_config['dates'],
        ]
        specific_fields = self._specific_fields()

        for s, i, d in itertools.product(*generic_fields):
            for fields in itertools.product(*specific_fields):
                for field in fields:
                    for fk, fv in field.items():
                        self._adapt_config(fk, fv)
                candles_cursor = CandleRetriever.get(s, i, d['df'], d['dt'])
                candles = list(candles_cursor)
                if not candles:
                    logging.warning('No klines')
                    continue
                logging.info(f'Calculating test: {s} - {i}')
                _, wallet = Strategist.calc(
                    candles, self.bt_config['strategy'])
                self._parse_output(wallet, s, i, d)

        self._persist_output()

    @staticmethod
    def _config(test_id):
        bt_config = Settings.BT
        bt_test = bt_config['tests'][test_id]
        bt_config.update(bt_test['override'])
        bt_config['strategy'] = bt_test['strategy']
        bt_config['header'] = bt_test['header']
        bt_config['dates'] = [
            {
                'df': utils.date_to_timestamp(d['df']),
                'dt': utils.date_to_timestamp(d['dt']),
            }
            for d in bt_config['dates']
        ]
        for test_bt_cfg_key, str_ind in bt_test['ranges'].items():
            for id_str_ind, config_dict in str_ind.items():
                for config_name, range_args in config_dict.items():
                    range_values = list(np.arange(*range_args))
                    bt_config[test_bt_cfg_key][id_str_ind][config_name] = (
                        range_values
                    )
        return bt_config

    def _set_header(self):
        self.test_specific_header = self.bt_config['header']
        self.output_header = (
            self.generic_header
            + self.wallet_header
            + self.test_specific_header
        )

    def _specific_fields(self):
        specific_fields = []
        strategy_id = self.bt_config['strategy']
        Strategy = Strategist.strategies[strategy_id]
        strategy_fields = self.bt_config['strategies'][strategy_id]
        for field_key, field_values in strategy_fields.items():
            fields = []
            key = self.sep.join([self.strat_prefix, strategy_id, field_key])
            for field_value in field_values:
                fields.append({key: field_value})
            specific_fields.append(fields)
        for Indicator in Strategy.indicators:
            indicator_id = Indicator._id
            indicator_fields = self.bt_config['indicators'][indicator_id]
            for field_key, field_values in indicator_fields.items():
                fields = []
                key = self.sep.join([self.ind_prefix, indicator_id, field_key])
                for field_value in field_values:
                    fields.append({key: field_value})
                specific_fields.append(fields)
        return specific_fields

    def _adapt_config(self, specific_field_key, specific_field_value):
        '''Adapts config before calculating the strategy with the new values'''
        str_or_ind, id_, field = specific_field_key.split(self.sep)
        s_i = (
            'strategies'
            if str_or_ind.startswith(self.strat_prefix)
            else 'indicators'
        )
        self.bt_config[s_i][id_][field] = specific_field_value
        self.bt_config[specific_field_key] = specific_field_value

    def _parse_output(self, wallet, symbol, interval, date):
        row = self._prepare_output_row(wallet, symbol, interval, date)
        if self.bt_config['output']['csv']['active']:
            self.output_rows.append(row)
        if self.bt_config['output']['mongo']['active']:
            db_insert.backtest(row)

    def _prepare_output_row(self, wallet, symbol, interval, date):
        specific_fields = {}
        for header in self.test_specific_header:
            value = self.bt_config[header]
            if type(value) == np.float64:
                value = float(value)
            if type(value) == np.int64:
                value = int(value)
            specific_fields[header] = value
        open_positions_long = 0
        close_positions_long = 0
        for position in wallet.positions_long:
            if position.action == 'open':
                open_positions_long += 1
            elif position.action == 'close':
                close_positions_long += 1
        profits = wallet.balance_origin - wallet.balance_origin_start
        profit_percentage = profits / (wallet.balance_origin_start / 100)
        row = {
            'test_id': self.test_id,
            'strategy': self.bt_config['strategy'],
            'symbol': symbol,
            'interval': interval,
            'df': str(utils.timestamp_to_date(date['df'])).split(' ')[0],
            'dt': str(utils.timestamp_to_date(date['dt'])).split(' ')[0],
            'test_date': self.test_date,
            'profit_percentage': profit_percentage,
            'balance_origin_start': wallet.balance_origin_start,
            'balance_origin_end': wallet.balance_origin,
            'amount_to_open': wallet.amount_to_open,
            'balance_long': wallet.balance_long,
            'open_positions_long': open_positions_long,
            'close_positions_long': close_positions_long,
            'total_payed_fees': wallet.stats.total_payed_fees,
            **specific_fields,
        }
        return row

    def _persist_output(self):
        if self.bt_config['output']['csv']['active']:
            with open(self.bt_config['output']['csv']['path'], 'w') as fd:
                csvdict = csv.DictWriter(fd, fieldnames=self.output_header)
                csvdict.writeheader()
                rows = sorted(
                    self.output_rows,
                    key=lambda r: r['balance_origin_end'],
                    reverse=True,
                )
                csvdict.writerows(rows)
