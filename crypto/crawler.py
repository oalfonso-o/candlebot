import logging

from crypto.endpoints import market_data  # noqa
from crypto import constants  # noqa
from crypto import mongo

logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self):
        self.mongo_conn = mongo.connect()

    def get_data(self, symbol):
        return 'None'
