import requests
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def parse_binance(response):
    response_data = response.json()
    return response_data['price']


def parse_poloniex(response):
    response_data = response.json()
    return response_data['result']['data'][-1]['c']


class Market:

    BINANCE = 'binance'
    POLONIEX = 'poloniex'

    APIS = {
        BINANCE: {
            'endpoint': 'https://api3.binance.com/api/v3/avgPrice?symbol={symbol}',  # noqa
            'parser': parse_binance,
            'symbols': ['ADAUSDT'],
        },
        POLONIEX: {
            'endpoint': 'https://api.crypto.com/v2/public/get-candlestick?instrument_name={symbol}&timeframe=1m',  # noqa
            'parser': parse_poloniex,
            'symbols': ['ADA_USDT'],
        },
    }

    @classmethod
    def compare(cls):
        cls._fill_symbols()
        market_status = defaultdict(dict)
        for name, data in cls.APIS.items():
            for symbol in data['symbols']:
                uri = data['endpoint'].format(symbol=symbol)
                response = requests.get(uri)
                try:
                    market_value = data['parser'](response)
                except Exception:
                    logging.exception(f'Request error: {name}, {symbol}')
                market_status[name][symbol] = market_value
        return market_status

    @classmethod
    def _fill_symbols(cls):  # TODO: fill cls.APIS[i]['symbols'] with api calls
        pass
