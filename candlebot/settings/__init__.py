import os
import yaml
import pymongo
import logging
import urllib.parse
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)


class Settings:

    API_KEY = os.getenv('CANDLEBOT_API_KEY')
    SECRET_KEY = os.getenv('CANDLEBOT_SECRET_KEY')

    if not API_KEY or not SECRET_KEY:
        raise EnvironmentError(
            'CANDLEBOT_API_KEY and CANDLEBOT_SECRET_KEY must be defined')

    MONGO_HOST = os.getenv('CANDLEBOT_MONGO_HOST')
    MONGO_PORT = os.getenv('CANDLEBOT_MONGO_PORT')
    MONGO_DATABASE = os.getenv('CANDLEBOT_MONGO_DATABASE', 'candlebot')
    MONGO_USER = os.getenv('CANDLEBOT_MONGO_USER')
    MONGO_PWD = os.getenv('CANDLEBOT_MONGO_PWD')

    MONGO_CONN = None

    api_origins = os.getenv('CANDLEBOT_API_ORIGINS')
    API_ORIGINS = api_origins.split(',') if api_origins else ['http://localhost:1234']  # noqa

    bt_config_file = (
        os.getenv('CANDLEBOT_BT_CONFIG_FILE') or '../backtesting.yml')
    with open(bt_config_file) as fd:
        BT = yaml.load(fd, Loader=yaml.SafeLoader)

    @classmethod
    def db_connect(cls):
        host = cls.MONGO_HOST
        port = cls.MONGO_PORT
        user = cls.MONGO_USER
        passwd = cls.MONGO_PWD
        if user and passwd:
            quoted_user = urllib.parse.quote_plus(user)
            quoted_passwd = urllib.parse.quote_plus(passwd)
            uri = f'mongodb://{quoted_user}:{quoted_passwd}@{host}:{port}'
        else:
            uri = f'mongodb://{host}:{port}'
        cls.MONGO_CONN = pymongo.MongoClient(uri)
        cls.MONGO_CONN.server_info()
        logger.info(f'PyMongo client connected to {host}:{port}')


if not Settings.MONGO_CONN:
    Settings.db_connect()
