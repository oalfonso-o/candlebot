import logging

from crypto.db import connection
from crypto import settings
from crypto import constants

logger = logging.getLogger(__name__)


def find(symbol, query, fields):
    coll_name = constants.MONGO_COLLS[symbol]
    mongo_coll = connection[settings.MONGO_DATABASE][coll_name]
    return mongo_coll.find(query, fields)
