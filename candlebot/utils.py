import datetime

from candlebot import constants


def str_to_date(date):
    return datetime.datetime.strptime(date, constants.DATE_ARG_FORMAT)


def date_to_timestamp(date):
    return int(str_to_date(date).timestamp()) * constants.DATE_MILIS_PRODUCT


def datetime_to_timestamp(date):
    return int(date.timestamp()) * constants.DATE_MILIS_PRODUCT


def timestamp_to_date(timestamp):
    parsed_timestamp = int(timestamp) / constants.DATE_MILIS_PRODUCT
    return datetime.datetime.fromtimestamp(parsed_timestamp)
