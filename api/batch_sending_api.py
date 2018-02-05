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
    传入的格式
    {
      "sending_task_id": 1,
      "task_covering_chatroom_count": 12,
      "task_covering_people_count": 1321,
      "task_sended_count": 1,
      "task_sended_failed_count": 3,
      "task_create_time": ,
      "chatroom_list": [
        {
          "chatroom_id": 2,
          "chatroom_nickname": "一个小群",
          "chatroom_member_count": 145,
          "chatroom_avatar": "",
          "chatroom_status": 0
        },
        {
          "chatroom_id": 5,
          "chatroom_nickname": "另一个小群",
          "chatroom_member_count": 213,
          "chatroom_avatar": "",
          "chatroom_status": 0
        }
      ],
      "message_list": [
        {
          "material_id": 1,
          "task_send_type": 1,
          "task_send_content": {
            "text": "这是一段发送的文字。这段文字不能太长，但是预计可以在500字以内"
          }
        },
        {
          "material_id": 1,
          "task_send_type": 2,
          "task_send_content": {
            "title": "一个美丽的图片或者什么的",
            "description": "一张图片的描述",
            "url": "http:"
          }
        }
      ]
    }
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
