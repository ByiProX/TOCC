# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api_v2, ERR_WRONG_FUNC_STATUS
from core_v2.batch_sending_core import get_batch_sending_task, get_task_detail, create_a_sending_task
from core_v2.user_core import UserLogin
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api_v2.route('/get_batch_sending_task', methods=['POST'])
def app_get_batch_sending_task():
    """
    得到主界面所需的所有信息
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # TODO: 结构修改
    task_per_page = request.json.get('page_size')
    page_number = request.json.get('page')
    task_status = request.json.get("status")
    if not task_per_page:
        logger.warning("没有收到page_size，设置为10")
        task_per_page = 10
    if page_number is None:
        logger.warning("没有收到page_number，设置为0")
        page_number = 0

    # if not user_info.func_send_qun_messages:
    #     return make_response(ERR_WRONG_FUNC_STATUS)

    status, res, total_count = get_batch_sending_task(user_info, task_per_page, page_number, task_status)
    if status == SUCCESS:
        return make_response(SUCCESS, task_info=res, total_count = total_count)
    else:
        return make_response(status)


@main_api_v2.route('/get_task_detail', methods=['POST'])
def app_get_task_detail():
    """
    查看任务详情
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # if not user_info.func_send_qun_messages:
    #     return make_response(ERR_WRONG_FUNC_STATUS)

    # TODO: 结构修改
    batch_send_task_id = request.json.get('batch_send_task_id')
    if not batch_send_task_id:
        return make_response(ERR_PARAM_SET)

    status, res = get_task_detail(batch_send_task_id)
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

    # if not user_info.func_send_qun_messages:
    #     return make_response(ERR_WRONG_FUNC_STATUS)

    sending_task_id = request.json.get('sending_task_id')
    if not sending_task_id:
        return make_response(ERR_PARAM_SET)

    raise NotImplementedError


@main_api_v2.route('/create_a_sending_task', methods=['POST'])
def app_create_a_sending_task():
    """
    创建一个任务
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # if not user_info.func_send_qun_messages:
    #     return make_response(ERR_WRONG_FUNC_STATUS)

    chatroom_list = request.json.get('chatroom_list')
    if not chatroom_list:
        return make_response(ERR_PARAM_SET)
    message_list = request.json.get('message_list')
    if not message_list:
        return make_response(ERR_PARAM_SET)

    status = create_a_sending_task(user_info, chatroom_list, message_list)

    return make_response(status)
