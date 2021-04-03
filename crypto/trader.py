import logging

from crypto import constants  # noqa
from crypto import mongo

logger = logging.getLogger(__name__)


class Trader:

    def __init__(self):
        self.mongo_conn = mongo.connect()

    def trade(self, symbol):
        logger.info(f'Trading {symbol}')
        return 'None'
