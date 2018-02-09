# -*- coding: utf-8 -*-

from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api, ERR_WRONG_FUNC_STATUS
from core.batch_sending_core import create_a_sending_task, get_task_detail, get_batch_sending_task
from core.user_core import UserLogin
from utils.u_response import make_response


@main_api.route('/get_batch_sending_task', methods=['POST'])
def app_get_batch_sending_task():
    """
    得到主界面所需的所有信息
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    if not user_info.func_send_qun_messages:
        return make_response(ERR_WRONG_FUNC_STATUS)

    status, res = get_batch_sending_task(user_info)
    if status == SUCCESS:
        return make_response(SUCCESS, task_info=res)
    else:
        return make_response(status)


@main_api.route('/get_task_detail', methods=['POST'])
def app_get_task_detail():
    """
    查看任务详情
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    if not user_info.func_send_qun_messages:
        return make_response(ERR_WRONG_FUNC_STATUS)

    sending_task_id = request.json.get('sending_task_id')
    if not sending_task_id:
        return make_response(ERR_PARAM_SET)

    status, res = get_task_detail(sending_task_id)
    if status == SUCCESS:
        return make_response(SUCCESS, task_info=res)
    else:
        return make_response(status)


def app_get_task_fail_detail():
    """
    查看任务失败详情
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    if not user_info.func_send_qun_messages:
        return make_response(ERR_WRONG_FUNC_STATUS)

    sending_task_id = request.json.get('sending_task_id')
    if not sending_task_id:
        return make_response(ERR_PARAM_SET)

    raise NotImplementedError


@main_api.route('/create_a_sending_task', methods=['POST'])
def app_create_a_sending_task():
    """
    创建一个任务
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    if not user_info.func_send_qun_messages:
        return make_response(ERR_WRONG_FUNC_STATUS)

    chatroom_list = request.json.get('chatroom_list')
    if not chatroom_list:
        return make_response(ERR_PARAM_SET)
    message_list = request.json.get('message_list')
    if not message_list:
        return make_response(ERR_PARAM_SET)

    status = create_a_sending_task(user_info, chatroom_list, message_list)

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)
