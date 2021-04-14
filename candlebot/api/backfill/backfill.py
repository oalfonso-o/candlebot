from candlebot import constants
from candlebot.db import db_find


def list_():
    backfills = []
    for symbol, colls in constants.MONGO_COLLS.items():
        backfill = {
            'name': symbol,
            'intervals': [],
        }
        for coll_name in colls.values():
            interval = db_find.find_backfill_data(coll_name)
            if interval:
                backfill['intervals'].append(interval)
        backfills.append(backfill)
    return backfills
