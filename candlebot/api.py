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
    strat_df, positions = Strategist.calc(candles, 'ema')
    candles = []
    ema = []
    balance_origin = []
    balance_long = []
    balance_short = []
    chart_positions = []
    index_positions = 0
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
        ema_line = {'time': time, 'value': c['ema']}
        candles.append(candle)
        ema.append(ema_line)

        if (
            index_positions < len(positions)
            and positions[index_positions].timestamp / 1000 == time
        ):
            point_balance_origin = {'time': time, 'value': positions[index_positions].balance_origin}  # noqa
            point_balance_long = {'time': time, 'value': positions[index_positions].balance_long}  # noqa
            point_balance_short = {'time': time, 'value': positions[index_positions].balance_short}  # noqa
            balance_origin.append(point_balance_origin)
            balance_long.append(point_balance_long)
            balance_short.append(point_balance_short)
            if positions[index_positions].action == 'open':
                point_open_position = {
                    'time': time,
                    'text': str(positions[index_positions].amount),
                    'position': 'belowBar',
                    'color': 'blue',
                    'shape': 'arrowUp',
                }
                chart_positions.append(point_open_position)
            if positions[index_positions].action == 'close':
                point_close_position = {
                    'time': time,
                    'text': str(positions[index_positions].amount),
                    'position': 'aboveBar',
                    'color': 'green',
                    'shape': 'arrowDown',
                }
                chart_positions.append(point_close_position)
            index_positions += 1
    return [
        {
            'id': 'main',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions
                },
                {
                    'type': 'lines',
                    'values': ema,
                    'color': '#999',
                    'lineType': 1,
                },
            ],
            'width': 1200,
            'height': 600,
        },
        {
            'id': 'balance_origin',
            'series': [
                {'type': 'lines', 'values': balance_origin, 'color': '#39f'},
            ],
            'width': 1200,
            'height': 100,
        },
        {
            'id': 'balance_long',
            'series': [
                {'type': 'lines', 'values': balance_long, 'color': '#f5a'},
            ],
            'width': 1200,
            'height': 100,
        },
        {
            'id': 'balance_short',
            'series': [
                {'type': 'lines', 'values': balance_short, 'color': '#941'},
            ],
            'width': 1200,
            'height': 100,
        },
    ]
