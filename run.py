import logging
import argparse
import time
from dotenv import load_dotenv

load_dotenv()
from crypto import db  # noqa
db.connect()

from crypto.crawler import Crawler  # noqa
from crypto.charter import Charter  # noqa
from crypto.trader import Trader  # noqa
from crypto import constants  # noqa


def crawl(symbol):
    logging.info(f'Crawling with {symbol}')
    while True:
        Crawler.crawl(symbol)
        time.sleep(constants.CRAWLING_SECONDS_WINDOW)


def charts(symbol):
    logging.info(f'Show charts with {symbol}')
    Charter.show_charts(symbol)


def trade(symbol):
    logging.info(f'Trading with {symbol}')
    Trader.trade(symbol)


def fill(symbol, date_from):
    if not date_from:
        raise ValueError('Parameter --date-from is required for fill command')
    logging.info(f'Filling {symbol} from {date_from}')
    while date_from:
        date_from = Crawler.fill(symbol, date_from)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=(
            '%(asctime)s %(name)16.16s %(funcName)10.10s %(levelname)7s: '
            '%(message)s'
        ),
        force=True,
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        choices=[
            constants.COMMAND_CRAWL,
            constants.COMMAND_CHARTS,
            constants.COMMAND_TRADE,
            constants.COMMAND_FILL,
        ],
    )
    parser.add_argument(
        '-s',
        '--symbol',
        required=True,
        choices=[
            constants.SYMBOL_CARDANO_EURO,
            constants.SYMBOL_BITCOIN_EURO,
            constants.SYMBOL_ETHEREUM_EURO,
        ],
    )
    parser.add_argument(
        '--date-from',
        help=(
            'Unix timestamp in miliseconds. Used when command is '
            f'{constants.COMMAND_FILL} as date from to '
            'query Binance API and perform an initial filling of the DB.'
        )
    )
    args = parser.parse_args()
    logging.info(f'Command {args.command} -s {args.symbol} launched.')
    if args.command == constants.COMMAND_CRAWL:
        crawl(args.symbol)
    elif args.command == constants.COMMAND_CHARTS:
        charts(args.symbol)
    elif args.command == constants.COMMAND_TRADE:
        trade(args.symbol)
    elif args.command == constants.COMMAND_FILL:
        fill(args.symbol, args.date_from)
    logging.info(f'Command {args.command} -s {args.symbol} finished.')
