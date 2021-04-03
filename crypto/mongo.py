import os
import pymongo
import logging
import urllib.parse

logger = logging.getLogger(__name__)


def connect():
    host = os.getenv('SV_MONGO_HOST')
    port = os.getenv('SV_MONGO_PORT')
    user = os.getenv('SV_MONGO_USER')
    passwd = os.getenv('SV_MONGO_PASSWD')
    if user and passwd:
        quoted_user = urllib.parse.quote_plus(user)
        quoted_passwd = urllib.parse.quote_plus(passwd)
        uri = f'mongodb://{quoted_user}:{quoted_passwd}@{host}:{port}'
    else:
        uri = f'mongodb://{host}:{port}'
    connection = pymongo.MongoClient(uri)
    connection.server_info()
    logger.info(f'PyMongo client connected to {host}:{port}')
    return connection
