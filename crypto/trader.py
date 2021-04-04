import logging

logger = logging.getLogger(__name__)


class Trader:

    EMA_WINDOW = 20

    def trade(symbol, interval):
        logger.info(f'Trading {symbol} {interval}')

    @classmethod
    def trade_history(cls, symbol, interval):
        logger.info(f'Trading {symbol} {interval}')
