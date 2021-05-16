import requests
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def is_trackable_symbol(symbol, banned_symbols=None):
    if not banned_symbols:
        banned_symbols = []
    symbol = symbol.lower()
    return (
        'usdt' in symbol
        and 'bear' not in symbol
        and 'bull' not in symbol
        and symbol not in banned_symbols
    )


class Binance:

    BANNED_SYMBOLS = ['bchsvusdt', 'hcusdt']

    @classmethod
    def parse_prices(cls, response, symbol=None):
        market_values = {}
        response_data = response.json()
        for data in response_data:
            symbol = data['symbol']
            if is_trackable_symbol(symbol, cls.BANNED_SYMBOLS):
                market_values[symbol] = float(data['price'])
        return market_values

    @staticmethod
    def parse_single_price(response):
        response_data = response.json()
        return float(response_data['price'])


class Crypto:

    BANNED_SYMBOLS = ['scusdt']

    @classmethod
    def parse_prices(cls, response, symbol=None):
        market_values = {}
        response_data = response.json()
        for data in response_data['result']['data']:
            symbol = data['i']
            if is_trackable_symbol(symbol, cls.BANNED_SYMBOLS):
                market_values[symbol] = float(data['a'])
        return market_values

    @staticmethod
    def parse_single_price(response):
        response_data = response.json()
        return float(response_data['result']['data']['a'])


class Poloniex:
    @staticmethod
    def parse_prices(response, symbol=None):
        market_values = {}
        response_data = response.json()
        for symbol, data in response_data.items():
            if is_trackable_symbol(symbol):
                market_values[symbol] = float(data['last'])
        return market_values


class Wazirx:
    @staticmethod
    def parse_prices(response, symbol=None):
        market_values = {}
        response_data = response.json()
        for symbol, data in response_data.items():
            if is_trackable_symbol(symbol):
                market_values[symbol] = float(data['last'])
        return market_values

    @staticmethod
    def parse_single_price(response):
        response_data = response.json()
        return float(response_data[0]['price'])


class Gateio:

    BANNED_SYMBOLS = ['bifiusdt']

    @classmethod
    def parse_prices(cls, response, symbol=None):
        market_values = {}
        response_data = response.json()
        for data in response_data:
            symbol = data['currency_pair']
            if is_trackable_symbol(symbol, cls.BANNED_SYMBOLS):
                market_values[symbol] = float(data['last'])
        return market_values

    @staticmethod
    def parse_single_price(response):
        response_data = response.json()
        return float(response_data[0]['last'])


class Bitmart:

    BANNED_SYMBOLS = ['linausdt', 'truusdt']

    @classmethod
    def parse_prices(cls, response, symbol=None):
        market_values = {}
        response_data = response.json()
        for data in response_data['data']['tickers']:
            symbol = data['symbol']
            if is_trackable_symbol(symbol, cls.BANNED_SYMBOLS):
                market_values[symbol] = float(data['last_price'])
        return market_values


class Market:

    MIN_BEST_PERCENT = 2

    BINANCE = 'binance'
    CRYPTO = 'crypto'
    POLONIEX = 'poloniex'
    WAZIRX = 'wazirx'
    GATEIO = 'gateio'
    BITMART = 'bitmart'

    APIS = {
        BINANCE: {  # symbol example: ADAUSDT
            'prices_endpoint': 'https://api3.binance.com/api/v3/ticker/price',
            'prices_parser': Binance.parse_prices,
            'single_price_endpoint': 'https://api3.binance.com/api/v3/avgPrice?symbol={symbol}',  # noqa
            'single_price_parser': Binance.parse_single_price,
            'single_price_endpoint_symbol_separator': '',
        },
        CRYPTO: {  # symbol example: ADA_USDT
            'prices_endpoint': 'https://api.crypto.com/v2/public/get-ticker',
            'prices_parser': Crypto.parse_prices,
            'single_price_endpoint': 'https://api.crypto.com/v2/public/get-ticker?instrument_name={symbol}',  # noqa
            'single_price_parser': Crypto.parse_single_price,
            'single_price_endpoint_symbol_separator': '_',
        },
        POLONIEX: {  # symbol example: ADA_USDT
            'prices_endpoint': 'https://poloniex.com/public?command=returnTicker',  # noqa
            'prices_parser': Poloniex.parse_prices,
            'single_price_endpoint': '',
        },
        WAZIRX: {  # symbol example: adausdt
            'prices_endpoint': 'https://api.wazirx.com/api/v2/tickers',
            'prices_parser': Wazirx.parse_prices,
            'single_price_endpoint': 'https://api.wazirx.com/api/v2/trades?market={symbol}&limit=1',  # noqa
            'single_price_parser': Wazirx.parse_single_price,
            'single_price_endpoint_symbol_separator': '',
            'single_price_endpoint_symbol_transform': str.lower,
        },
        GATEIO: {  # symbol example: ADA_USDT
            'prices_endpoint': 'https://api.gateio.ws/api/v4/spot/tickers',
            'prices_parser': Gateio.parse_prices,
            'single_price_endpoint': 'https://api.gateio.ws/api/v4/spot/tickers?currency_pair={symbol}',  # noqa
            'single_price_parser': Gateio.parse_single_price,
            'single_price_endpoint_symbol_separator': '_',
        },
        BITMART: {  # symbol example: ADA_USDT
            'prices_endpoint': 'https://api-cloud.bitmart.com/spot/v1/ticker',
            'prices_parser': Bitmart.parse_prices,
            'single_price_endpoint': '',
        },
    }

    @classmethod
    def compare(cls, recalc_perc=False):
        logger.info('Start comparing prices')
        cls.recalc_perc = recalc_perc
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

    @classmethod
    def _compare_reconciled_prices(cls, reconciled_prices):
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
                    if price < min_price['price']:
                        min_price = {'cex': cex, 'price': price}
                    elif price > max_price['price']:
                        max_price = {'cex': cex, 'price': price}
                compared_price['best'] = {
                    'low': min_price,
                    'high': max_price,
                }
                if min_price['price']:
                    compared_price['best_percent'] = cls._calc_percentage(
                        max_price['price'], min_price['price']
                    )
                if (
                    compared_price['best_percent'] > cls.MIN_BEST_PERCENT
                    and cls.recalc_perc
                ):
                    cls._recalculate_percentage(compared_price)
                if compared_price['best_percent'] > cls.MIN_BEST_PERCENT:
                    compared_prices.append(compared_price)
        return sorted(
            compared_prices,
            key=lambda x: x['best_percent'],
            reverse=True,
        )

    @staticmethod
    def _calc_percentage(max_price, min_price):
        return (
            (max_price - min_price)
            / min_price
            * 100
        )

    @classmethod
    def _recalculate_percentage(cls, compared_price):
        logger.info(f'Recalculating percentage for {compared_price["best"]}')
        logger.info(
            f'Symbol: {compared_price["symbol"]} - '
            f'% {compared_price["best_percent"]}'
        )
        low = compared_price['best']['low']
        high = compared_price['best']['high']
        low_price = low['price']
        high_price = high['price']

        low_cex_map = cls.APIS[low['cex']]
        low_endpoint = low_cex_map['single_price_endpoint']
        if low_endpoint:
            low_symbol = compared_price['symbol']
            low_symbol_separator = (
                low_cex_map['single_price_endpoint_symbol_separator'])
            if low_symbol_separator:
                low_symbol = low_symbol_separator.join([
                    low_symbol[:-4], low_symbol[-4:]
                ])
            if 'single_price_endpoint_symbol_transform' in low_cex_map:
                trans = low_cex_map['single_price_endpoint_symbol_transform']
                low_symbol = trans(low_symbol)
            low_uri = low_endpoint.format(symbol=low_symbol)
            low_parser = low_cex_map['single_price_parser']
            low_response = requests.get(low_uri)
            low_price = low_parser(low_response)

        high_cex_map = cls.APIS[high['cex']]
        high_endpoint = high_cex_map['single_price_endpoint']
        if high_endpoint:
            high_symbol = compared_price['symbol']
            high_symbol_separator = (
                high_cex_map['single_price_endpoint_symbol_separator'])
            if high_symbol_separator:
                high_symbol = high_symbol_separator.join([
                    high_symbol[:-4], high_symbol[-4:]
                ])
            if 'single_price_endpoint_symbol_transform' in high_cex_map:
                trans = high_cex_map['single_price_endpoint_symbol_transform']
                high_symbol = trans(high_symbol)
            high_uri = high_endpoint.format(symbol=high_symbol)
            high_parser = high_cex_map['single_price_parser']
            high_response = requests.get(high_uri)
            high_price = high_parser(high_response)

        if low_price and high_price:
            compared_price['best_percent'] = cls._calc_percentage(
                high_price, low_price
            )
