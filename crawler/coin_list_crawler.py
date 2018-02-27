# -*- coding: utf-8 -*-
import json

import decimal
import requests


# https://block.cc/api/v1/coin/list?page=0&size=5000
from datetime import datetime

from configs.config import db
from models.real_time_quotes_models import RealTimeQuotesDefaultSettingInfo


def get_coin_list():
    url = u"https://block.cc/api/v1/coin/list?page=0&size=5000"
    response = requests.get(url)
    coin_list = json.loads(response.content).get('data').get('list')
    return coin_list


def str_to_decimal(_str):
    if _str and _str != u'None':
        return decimal.Decimal(_str)
    else:
        return decimal.Decimal(u'0')


def update_coin_info():
    coin_list = get_coin_list()
    if len(coin_list) > 0:
        coin_list_already = db.session.query(RealTimeQuotesDefaultSettingInfo).all()
        coin_list_already_dict = {coin.symbol: coin for coin in coin_list_already}
        new_coin_symbol_set = set()
        for coin_json in coin_list:
            coin_id = coin_json.get(u'id')
            symbol = coin_json.get(u'symbol')
            coin_name = coin_json.get(u'name')
            coin_name_cn = coin_json.get(u'zhName')
            if coin_name_cn is None:
                coin_name_cn = u""

            available_supply = str_to_decimal(str(coin_json.get(u'available_supply')))
            change1d = str_to_decimal(str(coin_json.get(u'change1d')))
            change1h = str_to_decimal(str(coin_json.get(u'change1h')))
            change7d = str_to_decimal(str(coin_json.get(u'change7d')))
            price = str_to_decimal(str(coin_json.get(u'price')))
            volume_ex = str_to_decimal(str(coin_json.get(u'volume_ex')))
            marketcap = str_to_decimal(str(coin_json.get(u'marketCap')))
            suggest_ex1 = u""
            suggest_ex2 = u""
            suggest_ex1_url = u""
            suggest_ex2_url = u""
            suggest_ex_list = coin_json.get(u'suggest_ex')
            if len(suggest_ex_list) > 0:
                suggest_ex1 = suggest_ex_list[0].get(u'zh_name')
                suggest_ex1_url = suggest_ex_list[0].get(u'link')
                if len(suggest_ex_list) > 1:
                    suggest_ex2 = suggest_ex_list[1].get(u'zh_name')
                    suggest_ex2_url = suggest_ex_list[1].get(u'link')
            if symbol in new_coin_symbol_set:
                coin = coin_list_already_dict[symbol]
            elif symbol in coin_list_already_dict.keys():
                coin = coin_list_already_dict[symbol]
                db.session.merge(coin)
            else:
                coin = RealTimeQuotesDefaultSettingInfo(symbol, coin_name, coin_name_cn, coin_id, available_supply, change1d, change7d, change1h, price, volume_ex, marketcap, suggest_ex1, suggest_ex2, suggest_ex1_url, suggest_ex2_url)
                coin_list_already_dict[symbol] = coin
                new_coin_symbol_set.add(symbol)
                db.session.add(coin)

            print coin.coin_icon
        db.session.commit()

update_coin_info()
