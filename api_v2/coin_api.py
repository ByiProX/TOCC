# -*- coding: utf-8 -*-

import logging

from core_v2.real_time_quotes_core import switch_func_real_time_quotes, get_rt_quotes_list_and_status, \
    get_rt_quotes_preview
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api_v2, UserSwitch, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from models_v2.base_model import BaseModel
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api_v2.route('/switch_func_real_time_quotes', methods=['POST'])
def app_switch_func_real_time_quotes():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switch = request.json.get('switch')
    if not (switch is True or switch is False):
        return make_response(ERR_PARAM_SET)

    status = switch_func_real_time_quotes(user_info, switch)
    # logger.error("ERR_NOT_IMPLEMENTED 功能未实现，先留出口")

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api_v2.route('/get_rt_quotes_list_and_status', methods=['POST'])
def app_get_rt_quotes_list_and_status():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    task_per_page = request.json.get('pagesize')
    page_number = request.json.get('page')
    if not task_per_page:
        logger.warning("没有收到pagesize，设置为10")
        task_per_page = 10
    if page_number is None:
        logger.warning("没有收到page_number，设置为0")
        page_number = 0

    status, res, func_status, count = get_rt_quotes_list_and_status(user_info, task_per_page, page_number)

    if status == SUCCESS:
        return make_response(SUCCESS, coin_list=res, func_real_time_quotes=func_status, count=count)
    else:
        return make_response(status)


@main_api_v2.route('/get_func_real_time_quotes_status', methods=['POST'])
def app_get_func_real_time_quotes_status():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    user_switch = BaseModel.fetch_one(UserSwitch, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    if user_switch is None:
        logger.error("没有找到该用户的开关配置.")
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS, func_real_time_quotes=user_switch.func_real_time_quotes)


@main_api_v2.route('/get_rt_quotes_preview', methods=['POST'])
def app_get_rt_quotes_preview():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    coin_id = request.json.get('coin_id')
    if not coin_id:
        return make_response(ERR_PARAM_SET)

    status, res = get_rt_quotes_preview(coin_id)

    if status == SUCCESS:
        return make_response(SUCCESS, coin=res)
    else:
        return make_response(status)
