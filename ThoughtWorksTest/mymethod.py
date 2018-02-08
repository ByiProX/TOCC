#!/usr/bin/env python3
# coding = utf-8
# edit by iProX
# email: wangkx0105@outlook.com

import re
import math
from datetime import date


def get_car_info(li):
    """get information of cars into a dict"""
    # 将车辆信息转化为字典
    info = dict(zip(('plate_num', 'purchase_date', 'brand', 'miles_traveled', 'heavy_repair'),
                    (li.strip().split('|'))))
    return info


def get_date(li):
    """get date into a dict"""
    # 编辑获取日期的正则表达式
    date_pattern = re.compile(r'(20[0-9]{2})/(0[1-9]|1[012])/(0[1-9]|[12][0-9]|3[01])')

    # 将字符串表示的日期转化为字典型表示
    dates = dict(zip(('year', 'month', 'day'),
                     map(int, date_pattern.search(li).groups())))
    return dates


def count_month(li, submit_date):
    """read a line and count months"""
    purchase_date = get_date(li)

    # 计算相距月份数
    months_differ = abs((submit_date['year'] - purchase_date['year']) * 12 +
                        (submit_date['month'] - purchase_date['month']))
    return months_differ


def count_year(li, submit_date):
    """read a line and count years"""
    purchase_date = get_date(li)

    # 计算相距年份数
    years_differ = abs(submit_date['year'] - purchase_date['year'])
    return years_differ


def count_days(li, submit_date):
    """read a line and count years"""
    purchase_date = get_date(li)

    # 计算相距的天数
    days_differ = date(submit_date['year'], submit_date['month'], submit_date['day']) - \
                  date(purchase_date['year'], purchase_date['month'], purchase_date['day'])
    return days_differ.days


def is_write_off(li, submit_date):
    """read a line and judge whether to write off"""
    car_info = get_car_info(li)
    if car_info['heavy_repair'] == 'T':
        # 对大修车辆判断车是否已经报废
        if 3 * 365 - count_days(li, submit_date) <= 0:
            return 'wrote off'

        # 判断是否将要报废
        elif 0 <= 3 * 12 - count_month(li, submit_date) <= 1 or 0 < 365 * 3 - count_days(li, submit_date) <= 31:
            return True
        else:
            return False

    elif car_info['heavy_repair'] == 'F':
        # 对非大修车辆判断是否已经报废
        if 6 * 365 - count_days(li, submit_date) < 0:
            return 'wrote off'

        # 判断是否将要报废
        elif 0 <= 6 * 12 - count_month(li, submit_date) <= 1 or 0 < 365 * 6 - count_days(li, submit_date) <= 31:
            return True
        else:
            return False


def is_distance_related_maintain(li):
    """read a line and judge whether it is distance related maintain"""
    car_info = get_car_info(li)

    # 判断是否进行每一万公里保养提醒
    if math.ceil(int(car_info['miles_traveled']) / 10000) * 10000 - \
            int(car_info['miles_traveled']) <= 500:
        return True
    else:
        return False


def is_time_related_maintain(li, submit_date):
    """read a line and judge whether it is time related maintain"""
    car_info = get_car_info(li)
    if car_info['heavy_repair'] == 'T':
        # 对大修车辆判断是否进行定期保养
        if count_month(li, submit_date) % 3 in (0, 2):
            return True
        else:
            return False

    elif car_info['heavy_repair'] == 'F':
        # 对非大修、车龄三年及以上车辆判断是否进行定期保养
        if count_year(li, submit_date) >= 3:
            if count_month(li, submit_date) % 6 in (0, 5):
                return True
            else:
                return False

        # 对非大修、车龄三年以下车辆判断是否进行定期保养
        if count_year(li, submit_date) < 3:
            if count_month(li, submit_date) % 12 in (0, 11):
                return True
            else:
                return False


def print_result(dict1, dict2, dict3):
    """export as required"""
    # 对字典的键值(车辆品牌)按升序排序，并存储到列表中
    keys_of_dict1 = sorted(list(dict1.keys()))
    keys_of_dict2 = sorted(list(dict2.keys()))
    keys_of_dict3 = sorted(list(dict3.keys()))
    print('Reminder')
    print('=' * 18)

    print()
    print('* Time-related maintenance coming soon...')

    # 遍历字典打印相关结果
    for key in keys_of_dict1:
        print(key + ': ' + str(dict1[key]['num']) + ' (', end='')
        print(', '.join(plate for plate in dict1[key]['plate_num']), end='')
        print(')')

    print()
    print('* Distance-related maintenance coming soon...')

    # 遍历字典打印相关结果
    for key in keys_of_dict2:
        print(key + ': ' + str(dict2[key]['num']) + ' (', end='')
        print(', '.join(plate for plate in dict2[key]['plate_num']), end='')
        print(')')

    print()
    print('* Write-off maintenance coming soon...')

    # 遍历字典打印相关结果
    for key in keys_of_dict3:
        print(key + ': ' + str(dict3[key]['num']) + ' (', end='')
        print(', '.join(plate for plate in dict3[key]['plate_num']), end='')
        print(')')
