import datetime
import requests
import logging

from crypto.endpoints import market_data
from crypto import constants
from crypto.db import db_insert

logger = logging.getLogger(__name__)


class Crawler:
    url = (
        f'{constants.API_BASE_URL}'
        f'{constants.MARKET_DATA_SPOT_API_PREFIX}'
        f'{market_data["klines"]}'
    )
    interval = '1m'
    crawl_limit = 1
    fill_limit = 1000
    milis_product = 1000

    @classmethod
    def crawl(cls, symbol):
        params = {
            'symbol': symbol,
            'startTime': cls._timestamp(),
            'interval': cls.interval,
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
        db_insert.crawled_symbol(symbol, candlestick)

    @classmethod
    def fill(cls, symbol, date_from):
        params = {
            'symbol': symbol,
            'startTime': cls._timestamp(date_from),
            'interval': cls.interval,
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
        db_insert.crawled_symbols(symbol, candlesticks)

    @classmethod
    def _timestamp(cls, date_from=None):
        if not date_from:
            date_from = datetime.datetime.now().timestamp()
        two_minutes_ago = int(date_from) - 120
        timestamp = two_minutes_ago * cls.milis_product
        return timestamp
