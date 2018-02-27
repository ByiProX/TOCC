# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
from core.user_core import UserLogin
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api.route('/switch_func_synchronous_announcement', methods=['POST'])
def app_switch_func_synchronous_announcement():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switch = request.json.get('switch')
    if not (switch is True or switch is False):
        return make_response(ERR_PARAM_SET)

    status = SUCCESS
    logger.error("ERR_NOT_IMPLEMENTED 功能未实现，先留出口")

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('get_s_announcement_list_and_status', methods=['POST'])
def app_get_s_announcement_list_and_status():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    status = SUCCESS
    logger.error("ERR_NOT_IMPLEMENTED 功能未实现，先留出口")

    example = [
        {
            "platform_id": 1,
            "platform_name": "比特交易网",
            "is_take_effect": True
        },
        {
            "platform_id": 2,
            "platform_name": "库币网",
            "is_take_effect": False
        },
        {
            "platform_id": 3,
            "platform_name": "币交易",
            "is_take_effect": True
        },
    ]

    if status == SUCCESS:
        return make_response(SUCCESS, platform_list=example)
    else:
        return make_response(status)


@main_api.route('switch_a_s_announcement_effect', methods=['POST'])
def app_switch_a_s_announcement_effect():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switch = request.json.get('switch')
    if not (switch is True or switch is False):
        return make_response(ERR_PARAM_SET)

    status = SUCCESS
    logger.error("ERR_NOT_IMPLEMENTED 功能未实现，先留出口")

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)
