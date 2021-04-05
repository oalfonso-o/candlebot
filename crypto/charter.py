import logging

from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.graph_objects as go

from crypto.db.candle_retriever import CandleRetriever
from crypto.strategist import Strategist

logger = logging.getLogger(__name__)


class Charter:

    @staticmethod
    def chart_ema(
        symbol, interval, date_from=None, date_to=None, show_plot=True
    ):
        logger.info(f'Charting {symbol}_{interval} f:{date_from} t:{date_to}')
        candles_cursor = CandleRetriever.get(
            symbol, interval, date_from, date_to)
        candles = list(candles_cursor)
        if not candles:
            logging.warning('No klines')
            return {}
        strat_df, operations = Strategist.calc(candles, 'ema')
        if show_plot:
            candlestick = go.Candlestick(
                x=strat_df['_id'],
                open=strat_df['open'],
                high=strat_df['high'],
                low=strat_df['low'],
                close=strat_df['close'],
                name=symbol,
            )
            ema_scatter = go.Scatter(
                x=strat_df['_id'],
                y=strat_df['ema'],
                name='EMA',
                yaxis='y2',
            )
            buy_sell_scatter = go.Scatter(
                x=strat_df['_id'],
                y=strat_df['bs'],
                name='buy/sell',
                yaxis='y2',
                mode='markers',
                marker=dict(color='crimson', size=7),
            )
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(candlestick)
            fig.add_trace(ema_scatter, secondary_y=True)
            fig.add_trace(buy_sell_scatter, secondary_y=True)
            fig['layout'].update(title='EMA Chart', xaxis=dict(tickangle=-90))
            plot(fig)
        return operations
