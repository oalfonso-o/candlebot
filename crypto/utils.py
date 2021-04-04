import datetime

from crypto import constants


def str_to_date(date):
    return datetime.datetime.strptime(date, constants.DATE_ARG_FORMAT)


def date_to_timestamp(date):
    return int(str_to_date(date).timestamp()) * 1000


def timestamp_to_date(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp) / 1000)
