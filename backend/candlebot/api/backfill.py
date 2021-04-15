from fastapi import APIRouter
from pydantic import BaseModel

from candlebot import constants
from candlebot.db import db_find
from candlebot.crawler import Crawler
from candlebot import utils


router = APIRouter(
    prefix="/backfill",
    tags=["backfill"],
    responses={404: {"description": "Not found"}},
)


@router.get("/list")
async def backfill_list():
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


class BackfillBody(BaseModel):
    date_from: str
    date_to: str
    symbol: str
    interval: str


@router.post("/create")
async def backfill_create(body: BackfillBody):
    date_from_without_dash = body.date_from.replace('-', '')
    timestamp_date_from = utils.date_to_timestamp(date_from_without_dash)
    Crawler.fill(body.symbol, timestamp_date_from, body.interval)
    return 'Filled'
