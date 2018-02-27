# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
from core.user_core import UserLogin
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api.route('/switch_func_real_time_quotes', methods=['POST'])
def app_switch_func_real_time_quotes():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switch = request.json.get('switch')
    if not (switch is True or switch is False):
        return make_response(ERR_PARAM_SET)

    logger.error("ERR_NOT_IMPLEMENTED 功能未实现，先留出口")

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('get_rt_quotes_list_and_status', methods=['POST'])
def app_get_rt_quotes_list_and_status():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    status = SUCCESS
    logger.error("ERR_NOT_IMPLEMENTED 功能未实现，先留出口")

    example = [
        {
            "coin_id": 1,
            "coin_name": "比特币"
        },
        {
            "coin_id": 2,
            "coin_name": "以太坊"
        },
        {
            "coin_id": 3,
            "coin_name": "火币"
        },
    ]

    if status == SUCCESS:
        return make_response(SUCCESS, coin_list=example)
    else:
        return make_response(status)


@main_api.route('get_rt_quotes_preview', methods=['POST'])
def app_get_rt_quotes_preview():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    coin_id = request.json.get('coin_id')
    if not coin_id:
        return make_response(ERR_PARAM_SET)

    status = SUCCESS
    logger.error("ERR_NOT_IMPLEMENTED 功能未实现，先留出口")

    example = {
        "coin_id": coin_id,
        "coin_name": "比特币",
        "keyword_list": ["BTC", "btc", "比特币"],
        "reply":
            """
            比特币的当前价格为：￥11234.00
            当前市值：￥123亿
            市值排名：第1名
            流通数量：￥1234万
            推荐交易所：比特交易网
            24小时变化：-2.53%
            24小时成交额：￥124万
            【友问币答 2018-02-27 13:46:00】
            """
    }

    if status == SUCCESS:
        return make_response(SUCCESS, coin_list=example)
    else:
        return make_response(status)
