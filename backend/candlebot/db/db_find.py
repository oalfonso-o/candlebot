import logging
import datetime
from typing import Optional, List

from candlebot import utils
from candlebot import constants
from candlebot.settings import Settings

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


def find_last_backtests():
    mongo_coll = (
        Settings.MONGO_CONN[Settings.MONGO_DATABASE]
        [constants.MONGO_COLL_BACKTESTING]
    )
    sort = [
        ('test_date', -1),
        ('profit_percentage', -1),
        ('test_id', 1),
        ('strategy', 1),
        ('symbol', 1),
        ('interval', 1),
    ]
    backtests = list(mongo_coll.find({}, {'_id': 0}, sort=sort).limit(15))
    return backtests


def find_best_backtests():
    mongo_coll = (
        Settings.MONGO_CONN[Settings.MONGO_DATABASE]
        [constants.MONGO_COLL_BACKTESTING]
    )
    sort = [
        ('profit_percentage', -1),
        ('test_date', -1),
        ('test_id', 1),
        ('strategy', 1),
        ('symbol', 1),
        ('interval', 1),
    ]
    backtests = list(mongo_coll.find({}, {'_id': 0}, sort=sort).limit(15))
    return backtests


def find_filtered_backtests(
    test_id: Optional[str] = '',
    strategy: Optional[str] = '',
    symbols: List[str] = None,
    intervals: List[str] = None,
    sort_field: Optional[str] = 'profit_percentage',
    sort_direction: Optional[int] = -1,
    test_date_from: Optional[datetime.datetime] = None,
    test_date_to: Optional[datetime.datetime] = None,
    limit: Optional[int] = 15,
):
    mongo_coll = (
        Settings.MONGO_CONN[Settings.MONGO_DATABASE]
        [constants.MONGO_COLL_BACKTESTING]
    )
    query = {}
    sort = []
    if test_id:
        query['test_id'] = test_id
    if strategy:
        query['strategy'] = strategy
    if symbols:
        query['symbol'] = {'$in': symbols}
    if intervals:
        query['interval'] = {'$in': intervals}
    if test_date_from or test_date_to:
        query['test_date'] = {}
        if test_date_from:
            query['test_date']['$gte'] = test_date_from
        if test_date_to:
            query['test_date']['$lte'] = test_date_to
    if sort_field:
        sort = [(sort_field, sort_direction)]
    backtests = list(
        mongo_coll.find(query, {'_id': 0}, sort=sort).limit(limit)
    )
    return backtests


def available_symbols():
    colls = Settings.MONGO_CONN[Settings.MONGO_DATABASE].collection_names()
    return list({
        coll_name.split('_')[0]
        for coll_name in colls
        if '_' in coll_name
    })


def available_intervals():
    colls = Settings.MONGO_CONN[Settings.MONGO_DATABASE].collection_names()
    return list({
        coll_name.split('_')[1]
        for coll_name in colls
        if '_' in coll_name
    })
