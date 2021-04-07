import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
from candlebot import db  # noqa
db.connect()

from candlebot import utils  # noqa
from candlebot.db.candle_retriever import CandleRetriever  # noqa
from candlebot.strategist import Strategist  # noqa
from candlebot import constants  # noqa

app = FastAPI()
origins = ["http://localhost:1234"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    now = datetime.datetime.now()
    year_ago = datetime.datetime.now() - datetime.timedelta(days=356)
    candles_cursor = CandleRetriever.get(
        'ETHUSDT',
        '1d',
        utils.datetime_to_timestamp(year_ago),
        utils.datetime_to_timestamp(now),
    )
    candles = []
    for c in candles_cursor:
        c['time'] = c.pop('_id') / constants.DATE_MILIS_PRODUCT
        candles.append(c)
    return candles


@app.get("/ema")
async def ema():
    now = datetime.datetime.now()
    year_ago = datetime.datetime.now() - datetime.timedelta(days=356)
    candles_cursor = CandleRetriever.get(
        'ETHUSDT',
        '1d',
        utils.datetime_to_timestamp(year_ago),
        utils.datetime_to_timestamp(now),
    )
    candles = list(candles_cursor)
    strat_df, stats = Strategist.calc(candles, 'ema')
    candles = []
    i_ema = []
    bs = []
    for _, c in strat_df.iterrows():
        time = (
            utils.datetime_to_timestamp(c['_id'].to_pydatetime())
            / constants.DATE_MILIS_PRODUCT
        )
        candle = {
            'time': time,
            'open': c['open'],
            'close': c['close'],
            'high': c['high'],
            'low': c['low'],
            'volume': c['volume'],
        }
        ema_line = {'time': time, 'value': c['close']}
        if c['bs'] != c['bs']:
            c['bs'] = 0
        bs_point = {'time': time, 'value': c['bs']}
        candles.append(candle)
        i_ema.append(ema_line)
        bs.append(bs_point)
    return [
        {'type': 'candles', 'values': candles},
        {'type': 'lines', 'values': i_ema, 'color': '#af0'},
        {'type': 'lines', 'values': bs, 'color': '#0fa'},
    ]
