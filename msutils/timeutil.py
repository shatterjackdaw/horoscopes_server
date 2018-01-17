# -*- coding:utf-8 -*-
import datetime
import time

ZERO = datetime.timedelta(0)


class FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = datetime.timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO

def utc_mktime(utc_tuple):
    """
    Returns number of seconds elapsed since epoch
    Note that no timezone are taken into consideration.
    utc tuple must be: (year, month, day, hour, minute, second)
    """
    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return time.mktime(utc_tuple) - time.mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))


def datetime_to_timestamp(dt=None):
    """
    Converts a datetime object to UTC timestamp
    """
    dt = dt if dt else datetime.datetime.utcnow()
    assert isinstance(dt, datetime.datetime)
    return int(utc_mktime(dt.timetuple()))


def utc_day_seconds():
    return datetime_to_timestamp(utc_day_in_datetime())


def utc_time_seconds():
    return datetime_to_timestamp(datetime.datetime.utcnow())


def utc_day_in_datetime():
    now = datetime.datetime.utcnow()
    return datetime.datetime(now.year, now.month, now.day)


def datetime_to_ms_str():
    """
    将服务器时间转化为精确到毫秒的str
    :return: 20170704081615129517
    """
    now = datetime.datetime.utcnow()
    return now.strftime('%Y%m%d%H%M%S%f')


if __name__ == "__main__":
    print datetime_to_ms_str()
