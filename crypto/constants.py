API_BASE_URL = 'https://api.binance.com'
MARKET_DATA_SPOT_API_PREFIX = '/api/v3'
AUTH_HEADER = 'X-MBX-APIKEY'

SYMBOL_CARDANO = 'ADA'
SYMBOL_BITCOIN = 'BTC'
SYMBOL_ETHEREUM = 'ETH'
SYMBOL_EURO = 'EUR'
SYMBOL_CARDANO_EURO = f'{SYMBOL_CARDANO}{SYMBOL_EURO}'
SYMBOL_BITCOIN_EURO = f'{SYMBOL_BITCOIN}{SYMBOL_EURO}'
SYMBOL_ETHEREUM_EURO = f'{SYMBOL_ETHEREUM}{SYMBOL_EURO}'

COMMAND_CRAWL = 'crawl'
COMMAND_CHARTS = 'charts'
COMMAND_TRADE = 'trade'
COMMAND_FILL = 'fill'

CRAWLING_SECONDS_WINDOW = 60

MONGO_COLLS = {
    SYMBOL_CARDANO_EURO: 'ada_eur',
    SYMBOL_BITCOIN_EURO: 'btc_eur',
    SYMBOL_ETHEREUM_EURO: 'eth_eur',
}

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
