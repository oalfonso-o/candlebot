import logging

from crypto.db import connection
from crypto import settings
from crypto import constants

logger = logging.getLogger(__name__)


def crawled_symbol(symbol, data):
    coll_name = constants.MONGO_COLLS[symbol]
    mongo_coll = connection[settings.MONGO_DATABASE][coll_name]
    mongo_coll.replace_one({'_id': data['_id']}, data, upsert=True)
    logger.info(f'DB Insert: {symbol} - {data}')
