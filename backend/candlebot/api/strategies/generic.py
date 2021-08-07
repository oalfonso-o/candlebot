import logging

from candlebot import utils
from candlebot import constants
from candlebot.db.candle_retriever import CandleRetriever
from candlebot.strategist import Strategist
from candlebot.api.strategies.utils import (
    add_open_close_points_to_chart_positions,
    basic_charts_dict,
)

logger = logging.getLogger(__name__)


def calc(
    strategy, date_from=None, date_to=None, symbol='ADAEUR', interval='1d'
):
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
        return []
    strat_df, wallet = Strategist.calc(candles, strategy)
    log_wallet_stats(wallet)
    Strategy = Strategist.all_strats[strategy]
    candles = []
    chart_positions_long = []
    index_positions_long = 0
    lines_indicators = Strategy.indicators
    markers_indicators = Strategy.markers_indicators
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

        candles.append(candle)
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
                chart_positions_long,
            )
            index_positions_long += 1
        else:
            chart_positions_long.append({'time': time})
    charts = basic_charts_dict(candles, chart_positions_long)
    return charts


def log_wallet_stats(wallet):
    logger.info(f'wins: {wallet.stats.wins}')
    logger.info(f'losses: {wallet.stats.losses}')
    logger.info(f'win/lose: {wallet.stats.win_lose_ratio}')
    logger.info(f'final balance: {wallet.stats.balance}')
    logger.info(f'% earn: {wallet.stats.earn_percentage}%')
