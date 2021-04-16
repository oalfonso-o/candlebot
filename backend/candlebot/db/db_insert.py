import logging
from pymongo import ReplaceOne

from candlebot.settings import Settings
from candlebot import constants

logger = logging.getLogger(__name__)


def crawled_symbol(symbol, doc, interval):
    coll_name = constants.MONGO_COLLS[symbol][interval]
    mongo_coll = Settings.MONGO_CONN[Settings.MONGO_DATABASE][coll_name]
    mongo_coll.replace_one({'_id': doc['_id']}, doc, upsert=True)
    logger.info(f'DB Insert: {coll_name} - {doc}')


def crawled_symbols(symbol, docs, interval):
    coll_name = constants.MONGO_COLLS[symbol][interval]
    mongo_coll = Settings.MONGO_CONN[Settings.MONGO_DATABASE][coll_name]
    ops = [
        ReplaceOne({'_id': doc['_id']}, doc, upsert=True)
        for doc in docs
    ]
    result = mongo_coll.bulk_write(ops)
    result_dict = {
        'inserted_count': result.inserted_count,
        'matched_count': result.matched_count,
        'modified_count': result.modified_count,
        'upserted_count': result.upserted_count,
    }
    logger.info(f'DB Bulk Insert: {coll_name} - {result_dict}')


def backtest(doc):
    coll_name = constants.MONGO_COLL_BACKTESTING
    mongo_coll = Settings.MONGO_CONN[Settings.MONGO_DATABASE][coll_name]
    mongo_coll.insert_one(doc)
