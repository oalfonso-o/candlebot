import logging

from crypto import constants  # noqa
from crypto import mongo

logger = logging.getLogger(__name__)


class Charter:

    def __init__(self):
        self.mongo_conn = mongo.connect()

    def show_charts(self, symbol):
        logger.info(f'Trading {symbol}')
        return 'None'
