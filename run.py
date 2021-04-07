import logging
import argparse
import time
from dotenv import load_dotenv

load_dotenv()
from candlebot import db  # noqa
db.connect()

from candlebot.crawler import Crawler  # noqa
from candlebot.backtesting import Backtesting  # noqa
from candlebot import constants  # noqa
from candlebot import utils  # noqa


def crawl(symbol, interval):
    if not interval:
        raise ValueError(
            'Parameter --crawler-interval is required for crawl command')
    logging.info(f'Crawling with {symbol}')
    while True:
        Crawler.crawl(symbol, interval)
        time.sleep(constants.CRAWLING_SECONDS_WINDOW)


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


def fill_all():
    logging.info(f'Filling all')
    Crawler.fill_backtesting()


def backtesting(bt_test_id):
    if not bt_test_id:
        raise ValueError(
            'Parameter --bt-test-id is required for backtesting command')
    logging.info(f'Running Backtesting')
    bt = Backtesting(bt_test_id)
    bt.test()


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
            constants.COMMAND_FILL,
            constants.COMMAND_FILL_ALL,
            constants.COMMAND_BACKTESTING,
        ],
    )
    parser.add_argument(
        '-s',
        '--symbol',
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
        help='Str Binance candlesticks interval',
    )
    parser.add_argument(
        '--fill-date-from',
        type=lambda d: utils.date_to_timestamp(d),
        help=(
            'Date YYYYMMDD. Used when command is '
            f'{constants.COMMAND_FILL} as date from to '
            'query Binance API and perform an initial filling of the DB.'
        )
    )
    parser.add_argument(
        '--bt-test-id',
        help=f'Test ID to run with {constants.COMMAND_BACKTESTING}',
    )
    parser.add_argument(
        '--chart-no-show',
        action='store_true',
    )
    args = parser.parse_args()
    logging.info(f'Command {args.command} launched.')
    if args.command == constants.COMMAND_CRAWL:
        crawl(args.symbol, args.interval)
    elif args.command == constants.COMMAND_FILL:
        fill(args.symbol, args.fill_date_from, args.interval)
    elif args.command == constants.COMMAND_FILL_ALL:
        fill_all()
    elif args.command == constants.COMMAND_BACKTESTING:
        backtesting(args.bt_test_id)
    logging.info(f'Command {args.command} finished.')
