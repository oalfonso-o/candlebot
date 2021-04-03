import logging

from crypto import constants  # noqa

logger = logging.getLogger(__name__)


class Trader:

    def trade(symbol):
        logger.info(f'Trading {symbol}')
        return 'None'
