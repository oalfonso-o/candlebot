import logging
from pymongo import ReplaceOne

from crypto.db import connection
from crypto import settings
from crypto import constants

logger = logging.getLogger(__name__)


def crawled_symbol(symbol, doc):
    coll_name = constants.MONGO_COLLS[symbol]
    mongo_coll = connection[settings.MONGO_DATABASE][coll_name]
    mongo_coll.replace_one({'_id': doc['_id']}, doc, upsert=True)
    logger.info(f'DB Insert: {symbol} - {doc}')


def crawled_symbols(symbol, docs):
    coll_name = constants.MONGO_COLLS[symbol]
    mongo_coll = connection[settings.MONGO_DATABASE][coll_name]
    ops = [
        ReplaceOne(doc['_id'], doc, upsert=True)
        for doc in docs
    ]
    result = mongo_coll.bulk_write(ops)
    logger.info(f'DB Bulk Insert: {symbol} - {result}')
