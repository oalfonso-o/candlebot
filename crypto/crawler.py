import datetime
import requests
import logging

from crypto.endpoints import market_data
from crypto import constants
from crypto.db import db_insert

logger = logging.getLogger(__name__)


class Crawler:

    @staticmethod
    def crawl(symbol):
        url = (
            f'{constants.API_BASE_URL}'
            f'{constants.MARKET_DATA_SPOT_API_PREFIX}'
            f'{market_data["klines"]}'
        )
        two_minutes_ago = int(datetime.datetime.now().timestamp()) - 120
        timestamp = int(f'{two_minutes_ago}000')
        params = {
            'symbol': symbol,
            'startTime': timestamp,
            'interval': '1m',
            'limit': 1,
        }
        response = requests.get(url, params=params)
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
