# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from configs.config import SCOPE_YES


def datetime_to_timestamp_utc_8(a_datetime):
    return (a_datetime - datetime(1970, 1, 1, 8)).total_seconds()


def like_datetime_to_timestamp_utc_8(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    return (datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                     microsecond=microsecond) - datetime(1970, 1, 1, 8)).total_seconds() * 1000


def get_today_0(time = None):
    if time is None:
        time = datetime.now()
    today = datetime(year = time.year, month = time.month, day = time.day)
    return today


def get_time_window_by_scope(scope):
    start_time = datetime(year = 1970, month = 1, day = 1)
    end_time = datetime(year = 2099, month = 1, day = 1)
    if scope:  # scope == 0
        if scope == SCOPE_YES:
            end_time = get_today_0()
            start_time = end_time - timedelta(days = 1)
        else:
            end_time = get_today_0() + timedelta(days = 1)
            start_time = end_time - timedelta(days = scope)

    return start_time, end_time
