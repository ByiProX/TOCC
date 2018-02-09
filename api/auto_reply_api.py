# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api, ERR_WRONG_FUNC_STATUS
from core.auto_reply_core import create_a_auto_reply_setting, switch_func_auto_reply, delete_a_auto_reply_setting, \
    get_auto_reply_setting
from core.batch_sending_core import create_a_sending_task, get_task_detail, get_batch_sending_task
from core.user_core import UserLogin
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api.route('/create_a_auto_reply_setting', methods=['POST'])
def app_create_a_auto_reply_setting():
    """
    创建一个任务
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    if not user_info.func_auto_reply:
        return make_response(ERR_WRONG_FUNC_STATUS)

    chatroom_list = request.json.get('chatroom_list')
    if not chatroom_list:
        return make_response(ERR_PARAM_SET)
    message_list = request.json.get('message_list')
    if not message_list:
        return make_response(ERR_PARAM_SET)
    keyword_list = request.json.get('keyword_list')
    if not keyword_list:
        return make_response(ERR_PARAM_SET)

    status = create_a_auto_reply_setting(user_info, chatroom_list, message_list, keyword_list)
    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('/switch_func_auto_reply', methods=['POST'])
def app_switch_func_auto_reply():
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


@main_api.route('/get_auto_reply_setting', methods=['POST'])
def app_get_auto_reply_setting():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    if not user_info.func_auto_reply:
        return ERR_WRONG_FUNC_STATUS

    status, res = get_auto_reply_setting(user_info)
    if status == SUCCESS:
        return make_response(SUCCESS, setting_info=res)
    else:
        return make_response(status)


@main_api.route('/delete_a_auto_reply_setting', methods=['POST'])
def app_delete_a_auto_reply_setting():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    setting_id = request.json.get('setting_id')
    if not setting_id:
        return make_response(ERR_PARAM_SET)

    if not user_info.func_auto_reply:
        return ERR_WRONG_FUNC_STATUS

    status = delete_a_auto_reply_setting(user_info, setting_id)
    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)
