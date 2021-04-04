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


def crawl(symbol, interval):
    if not interval:
        raise ValueError(
            'Parameter --crawler-interval is required for crawl command')
    logging.info(f'Crawling with {symbol}')
    while True:
        Crawler.crawl(symbol, interval)
        time.sleep(constants.CRAWLING_SECONDS_WINDOW)


def charts(symbol, interval, date_from, date_to):
    logging.info(f'Show charts with {symbol}')
    Charter.show_charts(symbol, interval, date_from, date_to)


def trade(symbol, interval, history=False):
    logging.info(f'Trading with {symbol}')
    if not history:
        Trader.trade(symbol, interval)
    else:
        Trader.trade_history(symbol, interval)


def fill(symbol, date_from, interval):
    if not date_from:
        raise ValueError(
            'Parameter --fill-date-from is required for fill command')
    if not interval:
        raise ValueError(
            'Parameter --crawler-interval is required for fill command')
    logging.info(f'Filling {symbol} from {date_from}')
    while date_from:
        date_from = Crawler.fill(symbol, date_from, interval)


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
            constants.SYMBOL_CARDANO_USDT,
            constants.SYMBOL_BITCOIN_USDT,
            constants.SYMBOL_ETHEREUM_USDT,
        ],
    )
    parser.add_argument(
        '-i',
        '--interval',
        required=True,
        help='Str Binance candlesticks interval',
    )
    parser.add_argument(
        '--fill-date-from',
        help=(
            'Unix timestamp in miliseconds. Used when command is '
            f'{constants.COMMAND_FILL} as date from to '
            'query Binance API and perform an initial filling of the DB.'
        )
    )
    parser.add_argument(
        '--chart-date-from',
        help=(
            'Unix timestamp in miliseconds. Used when command is '
            f'{constants.COMMAND_CHARTS} as date from to '
            'query our database and select candlesticks from that date.'
        )
    )
    parser.add_argument(
        '--trade-history',
        action='store_true',
        help=(
            f'Used with {constants.COMMAND_CHARTS} to check trade strategies '
            'with history.'
        )
    )
    args = parser.parse_args()
    logging.info(f'Command {args.command} -s {args.symbol} launched.')
    if args.command == constants.COMMAND_CRAWL:
        crawl(args.symbol, args.interval)
    elif args.command == constants.COMMAND_CHARTS:
        charts(
            args.symbol, args.chart_date_from, args.chart_date_to,
            args.interval,
        )
    elif args.command == constants.COMMAND_TRADE:
        trade(args.symbol, args.trade_history)
    elif args.command == constants.COMMAND_FILL:
        fill(args.symbol, args.fill_date_from, args.interval)
    logging.info(f'Command {args.command} -s {args.symbol} finished.')
