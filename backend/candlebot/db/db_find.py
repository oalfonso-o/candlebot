import logging

from candlebot.settings import Settings
from candlebot import utils

logger = logging.getLogger(__name__)


def find_backfill_data(coll_name):
    mongo_coll = Settings.MONGO_CONN[Settings.MONGO_DATABASE][coll_name]
    count = mongo_coll.estimated_document_count()
    if count:
        first_doc = mongo_coll.find_one(
            {}, {'_id': 1}, sort=[('_id', 1)]) or {}
        last_doc = mongo_coll.find_one(
            {}, {'_id': 1}, sort=[('_id', -1)]) or {}
        date_from = first_doc.get('_id')
        date_to = last_doc.get('_id')
        backfill = {
            'id': coll_name.split('_')[1],
            'date_from': utils.timestamp_to_str_date(date_from),
            'date_to': utils.timestamp_to_str_date(date_to),
            'count': count,
        }
        return backfill
    return {}


def available_symbols():
    colls = Settings.MONGO_CONN[Settings.MONGO_DATABASE].collection_names()
    return list({
        coll_name.split('_')[0]
        for coll_name in colls
    })


def available_intervals():
    colls = Settings.MONGO_CONN[Settings.MONGO_DATABASE].collection_names()
    return list({
        coll_name.split('_')[1]
        for coll_name in colls
    })