from datetime import datetime
from time import time

default_date_format = '%Y-%m-%d %H:%M:%S.%f'
mysql_date_format = '%Y-%m-%d %H:%M:%S'


def parse_datetime(dt_str, dt_format=default_date_format):
    return datetime.strptime(dt_str, dt_format)


def format_datetime(dt, dt_format=default_date_format):
    return dt.strftime(dt_format)


def now():
    return datetime.now()


def now_formatted(dt_format=default_date_format):
    return now().strftime(dt_format)


def current_timestamp_milliseconds():
    return int(round(time() * 1000))


def any_datetime_in_list_expired(datetime_list, expire_days):
    for dt in datetime_list:
        diff = now() - dt
        if diff.days >= expire_days:
            return True
    return False

