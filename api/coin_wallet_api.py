# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
from core.coin_wallet_core import switch_func_coin_wallet
from core.qun_manage_core import get_chatroom_list_by_user_info
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

    status = switch_func_coin_wallet(user_info, switch)

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('/get_user_chatroom_list', methods=['POST'])
def app_get_user_chatroom_list():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # example = [
    #     {
    #         "chatroom_id": 1,
    #         "chatroom_nickname": "群的名字",
    #         "chatroom_member_count": 12,
    #         "chatroom_avatar": "",
    #         "chatroom_status": 0
    #     },
    #     {
    #         "chatroom_id": 2,
    #         "chatroom_nickname": "另一个群名字",
    #         "chatroom_member_count": 25,
    #         "chatroom_avatar": "",
    #         "chatroom_status": 0
    #     },
    # ]
    # status = SUCCESS

    status, chatroom_list = get_chatroom_list_by_user_info(user_info)

    if status == SUCCESS:
        return make_response(SUCCESS, chatroom_list=chatroom_list)
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
                "chatroom_id": 1,
                "member_id": 12,
                "member_nickname": "小号1",
                "member_avatar": "http://",
                "wallet_count": 1,
                "last_update_time": 10000,
                "wallets": [
                    {
                        "wallet_id": 1,
                        "coin_address": "0xsei64ge4s56g6s3aw4ta4tge5yehteig",
                        "is_origin": True,
                        "last_updated_time": 10000

                    }
                ]
            },
            {
                "chatroom_id": 1,
                "member_id": 13,
                "member_nickname": "小号1",
                "member_avatar": "http://",
                "wallet_count": 2,
                "last_update_time": 9997,
                "wallets": [
                    {
                        "wallet_id": 12,
                        "coin_address": "0xkyustuyhikset4g876ikse456w768i",
                        "is_origin": True,
                        "last_updated_time": 9997

                    },
                    {
                        "wallet_id": 1,
                        "coin_address": "0x87i6y2378tiq3gyujsdvghewrfgytu",
                        "is_origin": False,
                        "last_updated_time": 9992

                    }
                ]
            },
        ]
    else:
        example = [
            {
                "chatroom_id": 1,
                "member_id": 12,
                "member_nickname": "小号1",
                "member_avatar": "http://",
                "wallet_count": 1,
                "last_update_time": 10000,
                "wallets": [
                    {
                        "wallet_id": 1,
                        "coin_address": "0xsei64ge4s56g6s3aw4ta4tge5yehteig",
                        "is_origin": True,
                        "last_updated_time": 10000

                    }
                ]
            },
            {
                "chatroom_id": 2,
                "member_id": 14,
                "member_nickname": "小号1",
                "member_avatar": "http://",
                "wallet_count": 1,
                "last_update_time": 9998,
                "wallets": [
                    {
                        "wallet_id": 15,
                        "coin_address": "0x8i7yh32r47t634f7tuhifr768dsrg987",
                        "is_origin": True,
                        "last_updated_time": 9998

                    }
                ]
            },
            {
                "chatroom_id": 1,
                "member_id": 13,
                "member_nickname": "小号1",
                "member_avatar": "http://",
                "wallet_count": 2,
                "last_update_time": 9997,
                "wallets": [
                    {
                        "wallet_id": 12,
                        "coin_address": "0xkyustuyhikset4g876ikse456w768i",
                        "is_origin": True,
                        "last_updated_time": 9997

                    },
                    {
                        "wallet_id": 2,
                        "coin_address": "0x87i6y2378tiq3gyujsdvghewrfgytu",
                        "is_origin": False,
                        "last_updated_time": 9992

                    }
                ]
            },
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
                "chatroom_id": 1,
                "member_id": 18,
                "member_nickname": "小号1",
                "member_avatar": "http://",
            },
            {
                "chatroom_id": 1,
                "member_id": 22,
                "member_nickname": "小号2",
                "member_avatar": "http://",
            }
        ]
        count = 2
    else:
        # 读取该用户的所有成员
        example = [
            {
                "chatroom_id": 1,
                "member_id": 18,
                "member_nickname": "小号1",
                "member_avatar": "http://",
            },
            {
                "chatroom_id": 1,
                "member_id": 22,
                "member_nickname": "小号2",
                "member_avatar": "http://",
            },
            {
                "chatroom_id": 2,
                "member_id": 25,
                "member_nickname": "小号3",
                "member_avatar": "http://",
            }
        ]
        count = 3

    last_updated_time = 10000
    status = SUCCESS

    if status == SUCCESS:
        return make_response(SUCCESS, wallet_list=example, last_updated_time=last_updated_time, count=count)
    else:
        return make_response(status)
