import os
import yaml

API_KEY = os.getenv('CANDLEBOT_API_KEY')
SECRET_KEY = os.getenv('CANDLEBOT_SECRET_KEY')

if not API_KEY or not SECRET_KEY:
    raise EnvironmentError(
        f'CANDLEBOT_API_KEY and CANDLEBOT_SECRET_KEY must be defined')

MONGO_HOST = os.getenv('CANDLEBOT_MONGO_HOST')
MONGO_PORT = os.getenv('CANDLEBOT_MONGO_PORT')
MONGO_DATABASE = os.getenv('CANDLEBOT_MONGO_DATABASE', 'candlebot')
MONGO_USER = os.getenv('CANDLEBOT_MONGO_USER')
MONGO_PWD = os.getenv('CANDLEBOT_MONGO_PWD')

bt_config_file = os.getenv('CANDLEBOT_BT_CONFIG_FILE') or '../backtesting.yml'
with open(bt_config_file) as fd:
    BT = yaml.load(fd, Loader=yaml.SafeLoader)
