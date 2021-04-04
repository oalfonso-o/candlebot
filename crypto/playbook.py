from pprint import pprint

from crypto.charter import Charter
from crypto import utils
from crypto import constants


class Playbook:
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
        '1h',
        '1d',
    ]

    @classmethod
    def run(cls, print_results=True):
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
                play['symbol'], play['interval'], date_from, date_to
            )
        if print_results:
            for play in plays:
                play['results'] = play['results']['long_profit']
                pprint(play)
