import logging

from candlebot.settings import Settings
from candlebot import utils

logger = logging.getLogger(__name__)


def find_backfill_data(coll_name):
    mongo_coll = Settings.MONGO_CONN[Settings.MONGO_DATABASE][coll_name]
    count = mongo_coll.estimated_document_count()
    if count:
        first_doc = mongo_coll.find_one(
            {}, {'timestamp': 1}, sort=[('timestamp', 1)]) or {}
        last_doc = mongo_coll.find_one(
            {}, {'timestamp': 1}, sort=[('timestamp', -1)]) or {}
        date_from = first_doc.get('timestamp')
        date_to = last_doc.get('timestamp')
        backfill = {
            'id': coll_name.split('_')[1],
            'date_from': utils.timestamp_to_str_date(date_from),
            'date_to': utils.timestamp_to_str_date(date_to),
            'count': count,
        }
        return backfill
    return {}
