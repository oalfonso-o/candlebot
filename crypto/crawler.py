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
            f'{market_data["ticker_price"]}'
        )
        params = {'symbol': symbol}
        response = requests.get(url, params=params)
        value_datetime = datetime.datetime.now()
        data = response.json()
        data['datetime'] = value_datetime
        db_insert.crawled_symbol(symbol, data)
