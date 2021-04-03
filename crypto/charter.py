import logging

from crypto import constants  # noqa

logger = logging.getLogger(__name__)


class Charter:

    @staticmethod
    def show_charts(symbol):
        logger.info(f'Trading {symbol}')
        return 'None'
