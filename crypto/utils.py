import datetime

from crypto import constants


def str_to_date(date):
    return datetime.datetime.strptime(date, constants.DATE_ARG_FORMAT)


def date_to_timestamp(date):
    return int(str_to_date(date).timestamp()) * constants.DATE_MILIS_PRODUCT


def timestamp_to_date(timestamp):
    milis_timestamp = int(timestamp) / constants.DATE_MILIS_PRODUCT
    return datetime.datetime.fromtimestamp(milis_timestamp)
