import csv
import logging
from pprint import pprint

from crypto.charter import Charter
from crypto import utils
from crypto import constants
from crypto import settings

logger = logging.getLogger(__name__)


class Backtesting:
    symbols = [
        constants.SYMBOL_CARDANO_USDT,
        constants.SYMBOL_BITCOIN_USDT,
        constants.SYMBOL_ETHEREUM_USDT,
    ]
    dates = [
        {'f': '20170101', 't': '20180101'},
        {'f': '20180101', 't': '20190101'},
        {'f': '20190101', 't': '20200101'},
        {'f': '20200101', 't': '20210101'},
        {'f': '20210101', 't': '20220101'},
    ]
    intervals = [
        # '1h',
        '1d',
    ]
    output_fieldnames = [
        'symbol', 'interval', 'df', 'dt', 'buys', 'sells', 'long_profit',
        'short_profit', 'percent_long_profit'
    ]

    @classmethod
    def run(cls, print_results=False):
        plays = [
            {
                'results': {},
                'symbol': symbol,
                'interval': interval,
                'df': date['f'],
                'dt': date['t'],
            }
            for symbol in cls.symbols
            for interval in cls.intervals
            for date in cls.dates
        ]
        for play in plays:
            date_from = utils.date_to_timestamp(play['df'])
            date_to = utils.date_to_timestamp(play['dt'])
            play['results'] = Charter.show_charts(
                play['symbol'], play['interval'], date_from, date_to,
                show_plot=False
            )
        cls._output(plays)
        if print_results:
            for play in plays:
                if play['results']:
                    play['results'] = play['results']['long_profit']
                pprint(play)

    @classmethod
    def _output(cls, plays):
        rows = []
        with open(settings.BACKTESTING_OUTPUT, 'w') as fd:
            csvdict = csv.DictWriter(fd, fieldnames=cls.output_fieldnames)
            csvdict.writeheader()
            for play in plays:
                row = {
                    'symbol': play['symbol'],
                    'interval': play['interval'],
                    'df': str(utils.str_to_date(play['df'])).split(' ')[0],
                    'dt': str(utils.str_to_date(play['dt'])).split(' ')[0],
                    'buys': play['results'].get('buys') or 0,
                    'sells': play['results'].get('sells') or 0,
                    'long_profit': play['results'].get('long_profit') or 0,
                    'short_profit': play['results'].get('short_profit') or 0,
                    'percent_long_profit': '',
                }
                rows.append(row)
            rows = sorted(rows, key=lambda r: r['long_profit'], reverse=True)
            csvdict.writerows(rows)
        logger.info(f'Backtesting output in {settings.BACKTESTING_OUTPUT}')
