# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
from core.user_core import UserLogin
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api.route('/switch_func_coin_wallet', methods=['POST'])
def app_switch_func_coin_wallet():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switch = request.json.get('switch')
    if not (switch is True or switch is False):
        return make_response(ERR_PARAM_SET)

    # 样例数据
    status = SUCCESS

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('/get_user_chatroom_list', methods=['POST'])
def app_get_user_chatroom_list():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    example = [
        {
            "chatroom_id": 1,
            "chatroom_nickname": "群的名字",
            "chatroom_member_count": 12,
            "chatroom_avatar": "",
            "chatroom_status": 0
        },
        {
            "chatroom_id": 2,
            "chatroom_nickname": "另一个群名字",
            "chatroom_member_count": 25,
            "chatroom_avatar": "",
            "chatroom_status": 0
        },
    ]
    status = SUCCESS

    if status == SUCCESS:
        return make_response(SUCCESS, chatroom_list=example)
    else:
        return make_response(status)


@main_api.route('/get_members_coin_wallet', methods=['POST'])
def app_get_members_coin_wallet():
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

    uqun_id = request.json.get('chatroom_id')
    if uqun_id:
        # 读取该群的所有成员
        example = [
            {
                "wallet_id": 1,
                "wallet_owner_nickname": "惆怅旅客",
                "wallet_owner_avatar": "",
                "wallet_address": "",
                "wallet_updated_time": 10000
            },
            {
                "wallet_id": 2,
                "wallet_owner_nickname": "辣条小宫",
                "wallet_owner_avatar": "",
                "wallet_address": "",
                "wallet_updated_time": 9998
            }
        ]
    else:
        # 读取该用户的所有成员
        example = [
            {
                "wallet_id": 1,
                "wallet_owner_nickname": "惆怅旅客",
                "wallet_owner_avatar": "",
                "wallet_address": "",
                "wallet_updated_time": 10000
            },
            {
                "wallet_id": 2,
                "wallet_owner_nickname": "辣条小宫",
                "wallet_owner_avatar": "",
                "wallet_address": "",
                "wallet_updated_time": 9998
            },
            {
                "wallet_id": 3,
                "wallet_owner_nickname": "蓝毛怪",
                "wallet_owner_avatar": "",
                "wallet_address": "",
                "wallet_updated_time": 9995
            }
        ]

    last_updated_time = 10000
    status = SUCCESS

    if status == SUCCESS:
        return make_response(SUCCESS, wallet_list=example, last_updated_time=last_updated_time)
    else:
        return make_response(status)


@main_api.route('/update_a_coin_wallet', methods=['POST'])
def app_update_a_coin_wallet():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    wallet_id = request.json.get('wallet_id')
    if not wallet_id:
        return make_response(ERR_PARAM_SET)

    address_text = request.json.get("address_text")
    if not address_text:
        return make_response(ERR_PARAM_SET)

    status = SUCCESS

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('/delete_a_coin_wallet', methods=['POST'])
def app_delete_a_coin_wallet():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    wallet_id = request.json.get('wallet_id')
    if not wallet_id:
        return make_response(ERR_PARAM_SET)

    status = SUCCESS

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('/get_members_without_coin_wallet', methods=['POST'])
def app_get_members_without_coin_wallet():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    uqun_id = request.json.get('chatroom_id')
    if uqun_id:
        # 读取该群的所有成员
        example = [
            {
                "wallet_owner_nickname": "惆怅旅客",
                "wallet_owner_avatar": "",
            },
            {
                "wallet_owner_nickname": "辣条小宫",
                "wallet_owner_avatar": "",
            }
        ]
        count = 2
    else:
        # 读取该用户的所有成员
        example = [
            {
                "wallet_owner_nickname": "惆怅旅客",
                "wallet_owner_avatar": "",
            },
            {
                "wallet_owner_nickname": "辣条小宫",
                "wallet_owner_avatar": "",
            },
            {
                "wallet_owner_nickname": "蓝毛怪",
                "wallet_owner_avatar": "",
            }
        ]
        count = 3

    last_updated_time = 10000
    status = SUCCESS

    if status == SUCCESS:
        return make_response(SUCCESS, wallet_list=example, last_updated_time=last_updated_time, count=count)
    else:
        return make_response(status)

# # 现在不需要针对一个人的数据进行取得了
# @main_api.route('/get_a_member_coin_wallet_all_info', methods=['POST'])
# def app_a_member_coin_wallet_all_info():
#     status, user_info = UserLogin.verify_token(request.json.get('token'))
#     if status != SUCCESS:
#         return make_response(status)
#
#     wallet_id = request.json.get('wallet_id')
#     if not (wallet_id is True or wallet_id is False):
#         return make_response(ERR_PARAM_SET)
#
#     example = [
#         {
#             "wallet_id": 1,
#             "wallet_owner_nickname": "惆怅旅客",
#             "wallet_owner_avatar": "",
#             "wallet_address": "",
#             "wallet_updated_time": 10000
#         },
#         {
#             "wallet_id": 9,
#             "wallet_owner_nickname": "惆怅旅客",
#             "wallet_owner_avatar": "",
#             "wallet_address": "",
#             "wallet_updated_time": 9900
#         },
#         {
#             "wallet_id": 12,
#             "wallet_owner_nickname": "惆怅旅客",
#             "wallet_owner_avatar": "",
#             "wallet_address": "",
#             "wallet_updated_time": 9800
#         }
#     ]
#     status = SUCCESS
#
#     if status == SUCCESS:
#         return make_response(SUCCESS, wallet_list=example)
#     else:
#         return make_response(status)
