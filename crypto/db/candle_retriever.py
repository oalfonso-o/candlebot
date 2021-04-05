import logging

from crypto.db import connection
from crypto import settings
from crypto import constants

logger = logging.getLogger(__name__)


class CandleRetriever:
    def get(symbol, interval, date_from=None, date_to=None):
        query = {}
        if date_from or date_to:
            query = {'_id': {}}
            if date_from:
                query['_id']['$gte'] = int(date_from)
            if date_to:
                query['_id']['$lte'] = int(date_to)
        coll_name = constants.MONGO_COLLS[symbol][interval]
        mongo_coll = connection[settings.MONGO_DATABASE][coll_name]
        return mongo_coll.find(query, constants.KLINE_FIELDS)
