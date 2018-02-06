# -*- coding: utf-8 -*-

from datetime import datetime


def datetime_to_timestamp_utc_8(a_datetime):
    return (a_datetime - datetime(1970, 1, 1, 8)).total_seconds() * 1000


def like_datetime_to_timestamp_utc_8(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    return (datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                     microsecond=microsecond) - datetime(1970, 1, 1, 8)).total_seconds() * 1000
