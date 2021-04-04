import logging

from crypto import constants  # noqa

logger = logging.getLogger(__name__)


class Trader:

    def trade(symbol, interval):
        logger.info(f'Trading {symbol} {interval}')

    def trade_history(symbol, interval):
        logger.info(f'Trading {symbol} {interval}')
