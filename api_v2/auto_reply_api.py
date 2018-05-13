# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api_v2
from core_v2.auto_reply_core import create_a_auto_reply_setting, switch_func_auto_reply, \
    get_auto_reply_setting, delete_a_auto_reply_setting
from core_v2.user_core import UserLogin
from utils.u_model_json_str import verify_json
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api_v2.route('/create_a_auto_reply_setting', methods=['POST'])
def app_create_a_auto_reply_setting():
    """
    创建一个任务
    :return:
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    chatroom_list = request.json.get('chatroom_list')
    if not chatroom_list:
        return make_response(ERR_PARAM_SET)
    message_list = request.json.get('message_list')
    if not message_list:
        return make_response(ERR_PARAM_SET)
    keyword_list = request.json.get('keyword_list')
    if not keyword_list:
        return make_response(ERR_PARAM_SET)

    # 注：此处，如果有setting时，则意味着此处为修改，如果没有，则意味着此处为新建
    # 文法和磊的临时约定 BY FRank5433 20180210
    keywords_id = request.json.get('keywords_id')
    status = create_a_auto_reply_setting(user_info, chatroom_list, message_list, keyword_list, keywords_id = keywords_id)
    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api_v2.route('/switch_func_auto_reply', methods=['POST'])
def app_switch_func_auto_reply():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switch = request.json.get('switch')
    if not (switch is True or switch is False):
        return make_response(ERR_PARAM_SET)

    status = switch_func_auto_reply(user_info, switch)
    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api_v2.route('/get_auto_reply_setting', methods=['POST'])
def app_get_auto_reply_setting():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    status, res, func_auto_reply = get_auto_reply_setting(user_info)

    if status == SUCCESS:
        return make_response(SUCCESS, setting_info=res, func_auto_reply=func_auto_reply)
    else:
        return make_response(status)


@main_api_v2.route('/delete_a_auto_reply_setting', methods=['POST'])
def app_delete_a_auto_reply_setting():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    keywords_id = request.json.get('keywords_id')
    if not keywords_id:
        return make_response(ERR_PARAM_SET)

    status = delete_a_auto_reply_setting(user_info, keywords_id)
    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)
