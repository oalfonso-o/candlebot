import logging
import random
from collections import defaultdict

from candlebot import utils
from candlebot import constants
from candlebot.db.candle_retriever import CandleRetriever
from candlebot.strategist import Strategist
from candlebot.api.strategies.utils import (
    add_open_close_points_to_chart_positions,
    basic_charts_dict,
)

logger = logging.getLogger(__name__)

generic_colors = [
    'darkviolet', 'plum', 'orchid', 'mediumorchid', 'darkorchid', 'purple',
    'mediumpurple', 'mediumslateblue', 'blueviolet', 'darkmagenta',
    'darkgoldenrod', 'azure', 'beige', 'bisque',
    'blanchedalmond', 'cadetblue', 'chartreuse', 'cornsilk',
    'darkgreen', 'darkkhaki', 'darkolivegreen', 'darksalmon',
    'darkseagreen', 'forestgreen', 'gainsboro',
    'gold', 'goldenrod', 'green', 'greenyellow', 'honeydew',
    'ivory', 'khaki', 'lavender', 'lawngreen', 'lemonchiffon',
    'lime', 'limegreen',
    'mediumseagreen', 'mediumspringgreen', 'mistyrose', 'moccasin',
    'oldlace', 'olive', 'olivedrab', 'palegoldenrod',
    'palegreen', 'papayawhip', 'peachpuff', 'peru', 'seagreen', 'seashell',
    'silver', 'springgreen', 'tan', 'thistle',
    'wheat', 'yellow'
]

red_colors = [
    'brown', 'burlywood', 'chocolate', 'coral', 'crimson', 'darkorange',
    'darkred', 'deeppink', 'firebrick', 'fuchsia', 'hotpink', 'indianred',
    'magenta', 'maroon', 'orange', 'orangered', 'pink', 'red',
    'rosybrown', 'saddlebrown', 'salmon', 'sandybrown', 'sienna', 'tomato',
    'palevioletred', 'mediumvioletred', 'violet'
]

blue_colors = [
    'aliceblue', 'aqua', 'aquamarine', 'blue', 'cornflowerblue', 'cyan',
    'darkblue', 'darkcyan', 'darkslateblue', 'darkslategrey', 'darkturquoise',
    'deepskyblue', 'dodgerblue', 'indigo', 'lightblue', 'lightcyan',
    'lightseagreen', 'lightskyblue', 'mediumaquamarine', 'mediumblue',
    'mediumturquoise', 'midnightblue', 'navy', 'paleturquoise', 'powderblue',
    'royalblue', 'skyblue', 'slateblue', 'steelblue', 'teal', 'turquoise'
]


def calc(
    strategy, date_from=None, date_to=None, symbol='ADAEUR', interval='1d'
):
    ind_used_colors = set()
    if date_from and date_to:
        date_from_no_hyphen = date_from.replace('-', '')
        date_to_no_hyphen = date_to.replace('-', '')
        date_from = utils.date_to_timestamp(date_from_no_hyphen)
        date_to = utils.date_to_timestamp(date_to_no_hyphen)
    candles_cursor = CandleRetriever.get(
        symbol,
        interval,
        date_from,
        date_to,
    )
    candles = list(candles_cursor)
    if not candles:
        logger.warning('No candles!!!')
        return {}
    strat_df, wallet = Strategist.calc(candles, strategy)
    log_wallet_stats(wallet)
    Strategy = Strategist.strategies[strategy]
    candles = []
    index_positions_long = 0
    lines_indicators = Strategy.indicators
    markers_indicators = Strategy.markers_indicators
    lines_series_data = defaultdict(list)
    markers_series_data = []
    for _, c in strat_df.iterrows():
        time = get_time(c)
        candle = get_candle_dict(candle=c, time=time)
        candles.append(candle)
        index_positions_long = add_long_markers(
            index_positions_long=index_positions_long,
            wallet=wallet,
            time=time,
            markers_series_data=markers_series_data,
        )
        add_lines_series_data_points(
            indicators=lines_indicators,
            lines_series_data=lines_series_data,
            time=time,
            candle=c,
        )
        add_markers_series_data_points(
            indicators=markers_indicators,
            markers_series_data=markers_series_data,
            time=time,
            candle=c,
        )

    lines_series = get_lines_series(lines_series_data, ind_used_colors)
    charts = basic_charts_dict(candles, markers_series_data, lines_series)
    markers = {i._id: i.color for i in markers_indicators}
    markers['open'] = 'blue'  # TODO: don't harcode this
    markers['close'] = 'orange'
    stats = get_stats(wallet)
    return {
        'charts': charts,
        'stats': stats,
        'markers': markers,
    }


def get_time(candle):
    return (
        utils.datetime_to_timestamp(candle['_id'].to_pydatetime())
        / constants.DATE_MILIS_PRODUCT
    )


def get_candle_dict(candle, time):
    return {
        'time': time,
        'open': candle['open'],
        'close': candle['close'],
        'high': candle['high'],
        'low': candle['low'],
        'volume': candle['volume'],
    }


def log_wallet_stats(wallet):
    logger.info(f'wins: {wallet.stats.wins}')
    logger.info(f'losses: {wallet.stats.losses}')
    logger.info(f'win/lose: {wallet.stats.win_lose_ratio}')
    logger.info(f'final balance: {wallet.stats.balance}')
    logger.info(f'% earn: {wallet.stats.earn_percentage}%')


def add_long_markers(index_positions_long, wallet, time, markers_series_data):
    if (
        index_positions_long < len(wallet.positions_long)
        and (
            wallet.positions_long[index_positions_long].timestamp
            / 1000 == time
        )
    ):
        add_open_close_points_to_chart_positions(
            wallet.positions_long[index_positions_long],
            time,
            markers_series_data,
        )
        index_positions_long += 1
    else:
        markers_series_data.append({'time': time})
    return index_positions_long


def add_lines_series_data_points(indicators, lines_series_data, time, candle):
    for i in indicators:
        point = {'time': time, 'value': candle[i._id]}
        lines_series_data[i._id].append(point)


def add_markers_series_data_points(
    indicators, markers_series_data, time, candle
):
    for i in indicators:
        point = {'time': time}
        if candle[i._id]:
            point['text'] = i.text
            point['position'] = i.position
            point['color'] = i.color
            point['shape'] = i.shape
        markers_series_data.append(point)


def get_lines_series(lines_series_data, ind_used_colors):
    series = []
    for id_, data in lines_series_data.items():
        color = random.choice(generic_colors)
        while color in ind_used_colors:
            color = random.choice(generic_colors)
        ind_used_colors.add(color)
        serie = {
            'title': id_,
            'values': data,
            'color': color,
            'type': 'lines',
        }
        series.append(serie)
    return series


def get_stats(wallet):
    return {
        'wins': wallet.stats.wins,
        'losses': wallet.stats.losses,
        'win_lose_ratio': wallet.stats.win_lose_ratio,
        'earn': wallet.stats.earn_percentage,
    }
