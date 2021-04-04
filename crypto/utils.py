import datetime


def date_to_timestamp(date):
    return int(
        datetime.datetime.strptime(date, '%Y%m%d').timestamp()
    ) * 1000
