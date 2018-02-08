# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
from core.batch_sending_core import create_a_sending_task, get_task_detail, get_batch_sending_task
from core.user_core import UserLogin
from utils.u_response import make_response

logger = logging.getLogger('main')

@main_api.route('/get_batch_sending_task', methods=['POST'])
def app_get_batch_sending_task():
    """
    得到主界面所需的所有信息
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    task_per_page = request.json.get('page_size')
    page_number = request.json.get('page')
    if not task_per_page:
        logger.warning("没有收到page_size，设置为10")
        task_per_page = 10
    if page_number is None:
        logger.warning("没有收到page_number，设置为0")
        page_number = 0

    status, res = get_batch_sending_task(user_info, task_per_page,page_number)
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
