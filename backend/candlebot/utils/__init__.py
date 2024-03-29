import datetime

from candlebot import constants


def str_to_date(date):
    return datetime.datetime.strptime(date, constants.DATE_ARG_FORMAT)


def str_datetime_to_datetime(date):
    return datetime.datetime.strptime(date, constants.DATETIME_FORMAT)


def date_to_timestamp(date):
    return int(str_to_date(date).timestamp()) * constants.DATE_MILIS_PRODUCT


def datetime_to_timestamp(date):
    return int(date.timestamp()) * constants.DATE_MILIS_PRODUCT


def timestamp_to_date(timestamp):
    parsed_timestamp = int(timestamp) / constants.DATE_MILIS_PRODUCT
    return datetime.datetime.fromtimestamp(parsed_timestamp)


def timestamp_to_str_date(timestamp):
    return timestamp_to_date(timestamp).strftime('%Y/%m/%d')


def date_to_str_date(date):
    return date.strftime(constants.DATE_ARG_FORMAT)
