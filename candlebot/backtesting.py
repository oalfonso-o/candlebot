import csv
import logging
import datetime
import itertools

import numpy as np

from candlebot import utils
from candlebot import settings
from candlebot.db import db_insert
from candlebot.strategist import Strategist
from candlebot.db.candle_retriever import CandleRetriever

logger = logging.getLogger(__name__)


class Backtesting:
    generic_header = [
        'strategy',
        'symbol',
        'interval',
        'df',
        'dt',
    ]
    stats_header = [
        'buys',
        'sells',
        'long_profit',
        'short_profit',
        'long_profit_avg',
        'short_profit_avg',
    ]

    def __init__(self, test_id):
        self.output_rows = []
        date = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_mongo_coll = f'bt_{test_id}_{date}'
        self.bt_config = self._config(test_id)
        self.test_specific_header = self.bt_config['header']
        self.output_header = (
            self.generic_header
            + self.stats_header
            + self.test_specific_header
        )

    def test(self):
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
                _, stats = Strategist.calc(candles, self.bt_config['strategy'])
                self._parse_output(stats, s, i, d)

        self._persist_output()

    @staticmethod
    def _config(test_id):
        bt_config = settings.BT
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

    def _specific_fields(self):
        specific_fields = []
        strategy_id = self.bt_config['strategy']
        Strategy = Strategist.strategies[strategy_id]
        strategy_fields = self.bt_config['strategies'][strategy_id]
        for field_key, field_values in strategy_fields.items():
            fields = []
            key = f's.{strategy_id}.{field_key}'
            for field_value in field_values:
                fields.append({key: field_value})
            specific_fields.append(fields)
        for Indicator in Strategy.indicators:
            indicator_id = Indicator._id
            indicator_fields = self.bt_config['indicators'][indicator_id]
            for field_key, field_values in indicator_fields.items():
                fields = []
                key = f'i.{indicator_id}.{field_key}'
                for field_value in field_values:
                    fields.append({key: field_value})
                specific_fields.append(fields)
        return specific_fields

    def _adapt_config(self, specific_field_key, specific_field_value):
        '''Adapts config before calculating the strategy with the new values'''
        str_or_ind, id_, field = specific_field_key.split('.')
        s_i = 'strategies' if str_or_ind.startswith('s') else 'indicators'
        self.bt_config[s_i][id_][field] = specific_field_value
        self.bt_config[specific_field_key] = specific_field_value

    def _parse_output(self, stats, symbol, interval, date):
        row = self._prepare_output_row(stats, symbol, interval, date)
        if self.bt_config['output']['csv']['active']:
            self.output_rows.append(row)
        if self.bt_config['output']['mongo']['active']:
            db_insert.backtest(row, self.output_mongo_coll)

    def _prepare_output_row(self, stats, symbol, interval, date):
        specific_fields = {
            header: self.bt_config[header]
            for header in self.test_specific_header
        }
        row = {
            'strategy': self.bt_config['strategy'],
            'symbol': symbol,
            'interval': interval,
            'df': str(utils.timestamp_to_date(date['df'])).split(' ')[0],
            'dt': str(utils.timestamp_to_date(date['dt'])).split(' ')[0],
            'buys': stats.get('buys') or 0,
            'sells': stats.get('sells') or 0,
            'long_profit': stats.get('long_profit') or 0,
            'short_profit': stats.get('short_profit') or 0,
            'long_profit_avg': stats.get('long_profit_avg') or 0,
            'short_profit_avg': stats.get('short_profit_avg') or 0,
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
                    key=lambda r: r['long_profit_avg'],
                    reverse=True,
                )
                csvdict.writerows(rows)
