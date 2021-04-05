import datetime
import requests
import logging

from crypto.endpoints import market_data
from crypto import constants
from crypto.db import db_insert
from crypto import utils

logger = logging.getLogger(__name__)


class Crawler:
    url = (
        f'{constants.API_BASE_URL}'
        f'{constants.MARKET_DATA_SPOT_API_PREFIX}'
        f'{market_data["klines"]}'
    )
    crawl_limit = 1
    fill_limit = 1000
    symbols = [
        constants.SYMBOL_CARDANO_USDT,
        constants.SYMBOL_BITCOIN_USDT,
        constants.SYMBOL_ETHEREUM_USDT,
    ]
    intervals = ['1d', '1h']

    @classmethod
    def crawl(cls, symbol, interval):
        params = {
            'symbol': symbol,
            'startTime': cls._timestamp(),
            'interval': interval,
            'limit': cls.crawl_limit,
        }
        response = requests.get(cls.url, params=params)
        if not response.ok:
            logger.error(response['msg'])
            return
        data = response.json()
        if not data:
            return
        data = data[0]
        candlestick = {
            k: v
            for k, v in zip(constants.MAPPING_KLINES, data)
        }
        candlestick['_id'] = candlestick['timestamp']
        db_insert.crawled_symbol(symbol, candlestick, interval)

    @classmethod
    def fill(cls, symbol, date_from, interval):
        params = {
            'symbol': symbol,
            'startTime': date_from,
            'interval': interval,
            'limit': cls.fill_limit,
        }
        response = requests.get(cls.url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            logging.info('No more klines returned')
            return
        candlesticks = []
        for kline in data:
            candlestick = {
                k: v
                for k, v in zip(constants.MAPPING_KLINES, kline)
            }
            candlestick['_id'] = candlestick['timestamp']
            candlesticks.append(candlestick)
        db_insert.crawled_symbols(symbol, candlesticks, interval)
        return candlestick['timestamp'] + 1

    @classmethod
    def fill_backtesting(cls):
        for symbol in cls.symbols:
            for interval in cls.intervals:
                date_from = '20170101'
                date_from = utils.date_to_timestamp(date_from)
                while date_from:
                    date_from = cls.fill(
                        symbol=symbol,
                        date_from=date_from,
                        interval=interval,
                    )

    @classmethod
    def _timestamp(cls):
        timestamp_now = datetime.datetime.now().timestamp()
        two_minutes_ago = int(timestamp_now) - 120
        timestamp = two_minutes_ago * constants.DATE_MILIS_PRODUCT
        return timestamp
