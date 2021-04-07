import pymongo
import logging
import urllib.parse

from candlebot import settings

logger = logging.getLogger(__name__)

connection = None


def connect():
    global connection
    host = settings.MONGO_HOST
    port = settings.MONGO_PORT
    user = settings.MONGO_USER
    passwd = settings.MONGO_PWD
    if user and passwd:
        quoted_user = urllib.parse.quote_plus(user)
        quoted_passwd = urllib.parse.quote_plus(passwd)
        uri = f'mongodb://{quoted_user}:{quoted_passwd}@{host}:{port}'
    else:
        uri = f'mongodb://{host}:{port}'
    connection = pymongo.MongoClient(uri)
    connection.server_info()
    logger.info(f'PyMongo client connected to {host}:{port}')
