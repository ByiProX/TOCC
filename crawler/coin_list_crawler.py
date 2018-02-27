# -*- coding: utf-8 -*-
import json

import requests


# https://block.cc/api/v1/coin/list?page=0&size=5000
def get_coin_list():
    url = u"https://block.cc/api/v1/coin/list?page=0&size=1"
    # url = u"https://block.cc/api/v1/coin/list?page=0&size=5000"
    response = requests.get(url)
    print json.dumps(response.json())
    return json.loads(response.content)


coin_list = get_coin_list()
pass
