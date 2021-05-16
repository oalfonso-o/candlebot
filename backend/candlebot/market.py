import requests
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class Binance:
    @staticmethod
    def parse_prices(response, symbol=None):
        market_values = {}
        response_data = response.json()
        for data in response_data:
            symbol = data['symbol']
            if 'USDT' in symbol:
                market_values[symbol] = data['price']
        return market_values


class Crypto:
    @staticmethod
    def parse_prices(response, symbol=None):
        market_values = {}
        response_data = response.json()
        for data in response_data['result']['data']:
            symbol = data['i']
            if 'USDT' in symbol:
                market_values[symbol] = data['l']
        return market_values


class Poloniex:
    @staticmethod
    def parse_prices(response, symbol=None):
        market_values = {}
        response_data = response.json()
        for symbol, data in response_data.items():
            if 'USDT' in symbol:
                market_values[symbol] = data['last']
        return market_values


class Wazirx:
    @staticmethod
    def parse_prices(response, symbol=None):
        market_values = {}
        response_data = response.json()
        for symbol, data in response_data.items():
            if 'usdt' in symbol:
                market_values[symbol] = data['last']
        return market_values


class Gateio:
    @staticmethod
    def parse_prices(response, symbol=None):
        market_values = {}
        response_data = response.json()
        for data in response_data:
            symbol = data['currency_pair']
            if 'USDT' in symbol:
                market_values[symbol] = data['last']
        return market_values


class Market:

    BINANCE = 'binance'
    CRYPTO = 'crypto'
    POLONIEX = 'poloniex'
    WAZIRX = 'wazirx'
    GATEIO = 'gateio'

    APIS = {
        BINANCE: {
            'prices_endpoint': 'https://api3.binance.com/api/v3/ticker/price',
            'prices_parser': Binance.parse_prices,
        },
        CRYPTO: {
            'prices_endpoint': 'https://api.crypto.com/v2/public/get-ticker',
            'prices_parser': Crypto.parse_prices,
        },
        POLONIEX: {
            'prices_endpoint': 'https://poloniex.com/public?command=returnTicker',  # noqa
            'prices_parser': Poloniex.parse_prices,
        },
        WAZIRX: {
            'prices_endpoint': 'https://api.wazirx.com/api/v2/tickers',
            'prices_parser': Wazirx.parse_prices,
        },
        GATEIO: {
            'prices_endpoint': 'https://api.gateio.ws/api/v4/spot/tickers',
            'prices_parser': Gateio.parse_prices,
        },
    }

    @classmethod
    def compare(cls):
        logger.info('Start comparing prices')
        market_status = defaultdict(dict)
        for name, data in cls.APIS.items():
            logger.info(f'CEX: {name}')
            response = requests.get(data['prices_endpoint'])
            try:
                market_values = data['prices_parser'](response)
            except Exception:
                logging.exception(f'Request error: {name}')
            market_status[name] = market_values
        reconciled_prices = cls._reconcile_prices(market_status)
        compared_prices = cls._compare_reconciled_prices(reconciled_prices)
        return compared_prices

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
        nrmlzd_pair = pair.replace('_', '').upper()
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
                if float(min_price['price']):
                    compared_price['best_percent'] = (
                        (float(max_price['price']) - float(min_price['price']))
                        / float(min_price['price'])
                        * 100
                    )
                else:
                    logging.error(
                        f'{symbol}: max: {max_price} min: {min_price}. '
                        'Min price is 0.'
                    )
                compared_prices.append(compared_price)
        return sorted(
            compared_prices,
            key=lambda x: x['best_percent'],
            reverse=True,
        )
