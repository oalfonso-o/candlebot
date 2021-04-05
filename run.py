import logging
import argparse
import time
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
from crypto import db  # noqa
db.connect()

from crypto.crawler import Crawler  # noqa
from crypto.charter import Charter  # noqa
from crypto.trader import Trader  # noqa
from crypto.backtesting import Backtesting  # noqa
from crypto import constants  # noqa
from crypto import utils  # noqa


def crawl(symbol, interval):
    if not interval:
        raise ValueError(
            'Parameter --crawler-interval is required for crawl command')
    logging.info(f'Crawling with {symbol}')
    while True:
        Crawler.crawl(symbol, interval)
        time.sleep(constants.CRAWLING_SECONDS_WINDOW)


def charts(symbol, interval, date_from, date_to, chart_no_show):
    logging.info(f'Show charts with {symbol}')
    show_plot = not chart_no_show
    ops = Charter.ema(
        symbol, interval, date_from, date_to, show_plot=show_plot)
    if ops['long_profit_percents']:
        ops['long_profit_percents'] = (
            sum(ops['long_profit_percents'])
            / len(ops['long_profit_percents'])
        )
    if ops['short_profit_percents']:
        ops['short_profit_percents'] = (
            sum(ops['short_profit_percents'])
            / len(ops['short_profit_percents'])
        )
    pprint(ops)


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


def fill_all():
    logging.info(f'Filling all')
    Crawler.fill_backtesting()


def backtesting(backtesting_full_ema):
    logging.info(f'Running Backtesting')
    if not backtesting_full_ema:
        Backtesting.run()
    else:
        Backtesting.full_ema()


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
        '--chart-date-from',
        type=lambda d: utils.date_to_timestamp(d),
        help=(
            'Date YYYYMMDD. Used when command is '
            f'{constants.COMMAND_CHARTS} as date from to '
            'query our database and select candlesticks from that date.'
        )
    )
    parser.add_argument(
        '--chart-date-to',
        type=lambda d: utils.date_to_timestamp(d),
        help=(
           'Date YYYYMMDD. Used when command is '
           f'{constants.COMMAND_CHARTS} as date to for '
           'querying our database and select candlesticks before that date.'
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
    parser.add_argument(
        '--backtesting-full-ema',
        action='store_true',
        help=(
            f'Used with {constants.COMMAND_BACKTESTING} to check test all '
            'strategies and persist results to the DB.'
        )
    )
    parser.add_argument(
        '--chart-no-show',
        action='store_true',
    )
    args = parser.parse_args()
    logging.info(f'Command {args.command} launched.')
    if args.command == constants.COMMAND_CRAWL:
        crawl(args.symbol, args.interval)
    elif args.command == constants.COMMAND_CHARTS:
        charts(
            args.symbol, args.interval, args.chart_date_from,
            args.chart_date_to, args.chart_no_show
        )
    elif args.command == constants.COMMAND_TRADE:
        trade(args.symbol, args.trade_history)
    elif args.command == constants.COMMAND_FILL:
        fill(args.symbol, args.fill_date_from, args.interval)
    elif args.command == constants.COMMAND_FILL_ALL:
        fill_all()
    elif args.command == constants.COMMAND_BACKTESTING:
        backtesting(args.backtesting_full_ema)
    logging.info(f'Command {args.command} finished.')
