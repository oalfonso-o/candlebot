import os
import yaml

API_KEY = os.getenv('CRYPTO_API_KEY')
SECRET_KEY = os.getenv('CRYPTO_SECRET_KEY')

if not API_KEY or not SECRET_KEY:
    raise EnvironmentError(
        f'CRYPTO_API_KEY and CRYPTO_SECRET_KEY must be defined')

MONGO_HOST = os.getenv('CRYPTO_MONGO_HOST')
MONGO_PORT = os.getenv('CRYPTO_MONGO_PORT')
MONGO_DATABASE = os.getenv('CRYPTO_MONGO_DATABASE', 'crypto')
MONGO_USER = os.getenv('CRYPTO_MONGO_USER')
MONGO_PWD = os.getenv('CRYPTO_MONGO_PWD')

BT_OUTPUT = os.getenv('CRYPTO_BT_OUTPUT')
bt_config_file = os.getenv('CRYPTO_BT_CONFIG_FILE') or '../backtesting.yml'
with open(bt_config_file) as fd:
    BT_CONFIG = yaml.load(fd, Loader=yaml.SafeLoader)
