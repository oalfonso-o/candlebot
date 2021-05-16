import requests
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class Binance:
    @staticmethod
    def parse_price(response, symbol=None):
        response_data = response.json()
        return response_data['price']

    @staticmethod
    def parse_symbols(response, symbol=None):
        response_data = response.json()
        symbols = [
            symbol['symbol']
            for symbol in response_data['symbols'][:20]
            if 'USDT' in symbol['symbol']
        ]
        return symbols


class Crypto:
    @staticmethod
    def parse_price(response, symbol=None):
        response_data = response.json()
        return response_data['result']['data'][-1]['c']

    @staticmethod
    def parse_symbols(response, symbol=None):
        response_data = response.json()
        symbols = [
            symbol['instrument_name']
            for symbol in response_data['result']['instruments'][:10]
            if 'USDT' in symbol['instrument_name']
        ]
        return symbols


class Poloniex:
    @staticmethod
    def parse_price(response, symbol=None):
        market_values = {}
        response_data = response.json()
        for symbol, data in response_data.items():
            if 'USDT' in symbol:
                market_values[symbol] = data['last']
        return market_values


class Market:

    BINANCE = 'binance'
    CRYPTO = 'crypto'
    POLONIEX = 'poloniex'

    APIS = {
        BINANCE: {
            'price_endpoint': 'https://api3.binance.com/api/v3/avgPrice?symbol={symbol}',  # noqa
            'price_parser': Binance.parse_price,
            'symbols_endpoint': 'https://api3.binance.com/api/v3/exchangeInfo',
            'symbols_parser': Binance.parse_symbols,
            'symbols': [],
        },
        CRYPTO: {
            'price_endpoint': 'https://api.crypto.com/v2/public/get-candlestick?instrument_name={symbol}&timeframe=1m',  # noqa
            'price_parser': Crypto.parse_price,
            'symbols_endpoint': 'https://api.crypto.com/v2/public/get-instruments',  # noqa
            'symbols_parser': Crypto.parse_symbols,
            'symbols': [],
        },
        POLONIEX: {
            'price_endpoint': 'https://poloniex.com/public?command=returnTicker',  # noqa
            'price_parser': Poloniex.parse_price,
            'symbols_endpoint': '',
            'symbols_parser': None,
            'symbols': [],
        },
    }

    @classmethod
    def compare(cls):
        logger.info('Start comparing prices')
        market_status = defaultdict(dict)
        for name, data in cls.APIS.items():
            logger.info(f'CEX: {name}')
            if data['symbols_endpoint']:
                cls._fill_symbols(data)
                for symbol in data['symbols']:
                    uri = data['price_endpoint'].format(symbol=symbol)
                    market_value = cls._request_market_value(
                        uri, data['price_parser'], name, symbol)
                    market_status[name][symbol] = market_value
            else:  # poloniex endpoint returns data for all symbols
                response = requests.get(data['price_endpoint'])
                try:
                    market_values = data['price_parser'](response)
                except Exception:
                    logging.exception(f'Request error: {name}, {symbol}')
                market_status[name] = market_values
        reconciled_prices = cls._reconcile_prices(market_status)
        compared_prices = cls._compare_reconciled_prices(reconciled_prices)
        return compared_prices

    @classmethod
    def _fill_symbols(cls, data):
        symbols_response = requests.get(data['symbols_endpoint'])
        data['symbols'] = data['symbols_parser'](symbols_response)

    @classmethod
    def _request_market_value(cls, uri, parser, name, symbol=None):
        response = requests.get(uri)
        try:
            market_value = parser(response, symbol)
        except Exception:
            logging.exception(f'Request error: {name}, {symbol}')
        return market_value

    @classmethod
    def _reconcile_prices(cls, market_status):
        logger.info('Reconciling prices')
        pairs = defaultdict(list)
        for cex, market_values in market_status.items():
            for pair, value in market_values.items():
                nrmlzd_pair = cls._normalize_pair(pair)
                pairs[nrmlzd_pair].append({cex: value})
        return pairs

    @staticmethod
    def _normalize_pair(pair):
        nrmlzd_pair = pair.replace('_', '')
        if nrmlzd_pair.startswith('USDT'):
            nrmlzd_pair = nrmlzd_pair[4:] + nrmlzd_pair[:4]
        return nrmlzd_pair

    @staticmethod
    def _compare_reconciled_prices(reconciled_prices):
        logger.info('Calculate best price')
        compared_prices = []
        for symbol, prices in reconciled_prices.items():
            if len(prices) > 1:
                compared_price = {
                    'symbol': symbol,
                    'prices': prices,
                    'best_percent': 0,
                    'best': {
                        'low': {'price': 0, 'cex': ''},
                        'high': {'price': 0, 'cex': ''},
                    },
                }
                first_cex = list(prices[0].keys())[0]
                min_price = {'cex': first_cex, 'price': prices[0][first_cex]}
                max_price = min_price
                for item in prices[1:]:
                    cex = list(item.keys())[0]
                    price = item[cex]
                    if float(price) < float(min_price['price']):
                        min_price = {'cex': cex, 'price': price}
                    elif float(price) > float(max_price['price']):
                        max_price = {'cex': cex, 'price': price}
                compared_price['best'] = {
                    'low': min_price,
                    'high': max_price,
                }
                compared_price['best_percent'] = (
                    (float(max_price['price']) - float(min_price['price']))
                    / float(min_price['price'])
                    * 100
                )
                compared_prices.append(compared_price)
        return sorted(
            compared_prices,
            key=lambda x: x['best_percent'],
            reverse=True,
        )
