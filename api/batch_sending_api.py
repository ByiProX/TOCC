# -*- coding: utf-8 -*-

from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
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

    raise NotImplementedError


@main_api.route('/get_task_detail', methods=['POST'])
def app_get_task_detail():
    """
    查看任务详情
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    sending_task_id = request.json.get('sending_task_id')
    if not sending_task_id:
        return make_response(ERR_PARAM_SET)

    raise NotImplementedError


def app_get_task_fail_detail():
    """
    查看任务失败详情
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    sending_task_id = request.json.get('sending_task_id')
    if not sending_task_id:
        return make_response(ERR_PARAM_SET)

    raise NotImplementedError


@main_api.route('/get_batch_sending_task', methods=['POST'])
def app_create_a_sending_task():
    """
    创建一个任务
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    target_list = request.json.get('chatroom_list')
    if not target_list:
        return make_response(ERR_PARAM_SET)
    material_list = request.json.get('message_list')
    if not material_list:
        return make_response(ERR_PARAM_SET)

    raise NotImplementedError
