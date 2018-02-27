# -*- coding: utf-8 -*-
import json

import decimal
import requests


# https://block.cc/api/v1/coin/list?page=0&size=5000
def get_coin_list():
    url = u"https://block.cc/api/v1/coin/list?page=0&size=1"
    # url = u"https://block.cc/api/v1/coin/list?page=0&size=5000"
    response = requests.get(url)
    coin_list = json.loads(response.content).get('data').get('list')
    return coin_list


def update_coin_info():
    coin_list = get_coin_list()
    for coin in coin_list:
        symbol = coin.get(u'symbol')
        coin_name = coin.get(u'name')
        coin_name_cn = coin.get(u'zhName')
        available_supply = coin.get(u'available_supply')
        change1d = decimal.Decimal(coin.get(u'change1d'))
        change1h = decimal.Decimal(coin.get(u'change1h'))
        change7d = decimal.Decimal(coin.get(u'change7d'))
        price = decimal.Decimal(coin.get(u'price'))
        volume_ex = decimal.Decimal(coin.get(u'volume_ex'))
        marketcap = decimal.Decimal(coin.get(u'marketCap'))

        suggest_ex_list = coin.get(u'suggest_ex')
        if len(suggest_ex_list) > 0:
            suggest_ex1 = suggest_ex_list[0].get(u'zh_name')
            suggest_ex1_url = suggest_ex_list[0].get(u'link')
        if len(suggest_ex_list) > 1:
            suggest_ex2 = suggest_ex_list[1].get(u'zh_name')
            suggest_ex1_ur2 = suggest_ex_list[1].get(u'link')

    pass

update_coin_info()
