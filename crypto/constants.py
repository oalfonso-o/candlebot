API_BASE_URL = 'https://api.binance.com'
MARKET_DATA_SPOT_API_PREFIX = '/api/v3'
AUTH_HEADER = 'X-MBX-APIKEY'

SYMBOL_CARDANO = 'ADA'
SYMBOL_BITCOIN = 'BTC'
SYMBOL_ETHEREUM = 'ETH'
SYMBOL_EURO = 'EUR'
SYMBOL_USDT = 'USDT'
SYMBOL_CARDANO_EURO = f'{SYMBOL_CARDANO}{SYMBOL_EURO}'
SYMBOL_BITCOIN_EURO = f'{SYMBOL_BITCOIN}{SYMBOL_EURO}'
SYMBOL_ETHEREUM_EURO = f'{SYMBOL_ETHEREUM}{SYMBOL_EURO}'
SYMBOL_CARDANO_USDT = f'{SYMBOL_CARDANO}{SYMBOL_USDT}'
SYMBOL_BITCOIN_USDT = f'{SYMBOL_BITCOIN}{SYMBOL_USDT}'
SYMBOL_ETHEREUM_USDT = f'{SYMBOL_ETHEREUM}{SYMBOL_USDT}'

TRADING_SYMBOLS = [
    SYMBOL_CARDANO_EURO,
    SYMBOL_BITCOIN_EURO,
    SYMBOL_ETHEREUM_EURO,
    SYMBOL_CARDANO_USDT,
    SYMBOL_BITCOIN_USDT,
    SYMBOL_ETHEREUM_USDT,
]

INTERVALS = [
    '1m',
    '3m',
    '5m',
    '15m',
    '30m',
    '1h',
    '2h',
    '4h',
    '6h',
    '8h',
    '12h',
    '1d',
]

MONGO_COLLS = {
    symbol: {i: f'{symbol}_{i}' for i in INTERVALS}
    for symbol in TRADING_SYMBOLS
}
MONGO_COLL_BACKFILL_PLAYS = 'backtesting_plays'

COMMAND_CRAWL = 'crawl'
COMMAND_CHARTS = 'charts'
COMMAND_TRADE = 'trade'
COMMAND_FILL = 'fill'
COMMAND_FILL_ALL = 'fill_all'
COMMAND_BACKTESTING = 'backtesting'

CRAWLING_SECONDS_WINDOW = 60

MAPPING_KLINES = [
    'timestamp',
    'open',
    'high',
    'low',
    'close',
    'volume',
    'timestamp_close',
    'volume_quote',
    'trades_count',
    'volume_taker_base',
    'volume_taker_quote',
]
KLINE_FIELDS = {'open': 1, 'high': 1, 'low': 1, 'close': 1}

DATE_ARG_FORMAT = '%Y%m%d'
DATE_MILIS_PRODUCT = 1000
