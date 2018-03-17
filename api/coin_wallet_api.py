# -*- coding: utf-8 -*-

import logging

from datetime import datetime
from flask import request, send_file

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
from core.coin_wallet_core import switch_func_coin_wallet, get_members_coin_wallet_list, update_coin_address_by_id, \
    delete_wallet_by_id, get_members_without_coin_wallet, get_members
from core.qun_manage_core import get_chatroom_list_by_user_info
from core.user_core import UserLogin
from utils.u_response import make_response
from utils.u_time import datetime_to_timestamp_utc_8

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


@main_api.route('/get_coin_wallet_setting', methods=['POST'])
def app_get_coin_wallet_setting():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # status, res = get_coin_wallet_setting(user_info)

    if status == SUCCESS:
        return make_response(SUCCESS, func_coin_wallet=user_info.func_coin_wallet)
    else:
        return make_response(status)


@main_api.route('/get_members_coin_wallet', methods=['POST'])
def app_get_members_coin_wallet():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    limit = request.json.get('limit')
    offset = request.json.get('offset')
    if not limit:
        logger.warning("没有收到page_size，设置为10")
        limit = 10
    if offset is None:
        logger.warning("没有收到page_number，设置为0")
        offset = 0

    uqun_id = request.json.get('chatroom_id')
    status, wallet_list = get_members_coin_wallet_list(user_info = user_info, uqun_id = uqun_id,
                                                       limit = limit, offset = offset)
    last_updated_time = datetime_to_timestamp_utc_8(datetime.now())
    if wallet_list:
        last_updated_time = wallet_list[0].get('last_update_time')
    status = SUCCESS

    # 读取该群的所有成员
    if status == SUCCESS:
        return make_response(SUCCESS, wallet_list=wallet_list, last_updated_time=last_updated_time)
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

    status = update_coin_address_by_id(wallet_id, address_text)

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

    status = delete_wallet_by_id(wallet_id)

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('/get_members_without_coin_wallet', methods=['POST'])
def app_get_members_without_coin_wallet():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    limit = request.json.get('limit')
    offset = request.json.get('offset')
    if not limit:
        logger.warning("没有收到page_size，设置为10")
        limit = 10
    if offset is None:
        logger.warning("没有收到page_number，设置为0")
        offset = 0

    uqun_id = request.json.get('chatroom_id')
    status, member_list, count = get_members_without_coin_wallet(user_info = user_info, uqun_id = uqun_id,
                                                                 limit = limit, offset = offset)

    last_updated_time = datetime_to_timestamp_utc_8(datetime.now())
    if status == SUCCESS:
        return make_response(SUCCESS, member_list=member_list, last_updated_time=last_updated_time, count=count)
    else:
        return make_response(status)


@main_api.route('/search_coin_wallet', methods=['POST'])
def app_search_coin_wallet():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    limit = request.json.get('limit')
    offset = request.json.get('offset')
    if not limit:
        logger.warning("没有收到page_size，设置为10")
        limit = 10
    if offset is None:
        logger.warning("没有收到page_number，设置为0")
        offset = 0

    uqun_id = request.json.get('chatroom_id')
    keyword = request.json.get('keyword')
    status, member_list, count = get_members(user_info = user_info, uqun_id = uqun_id, limit = limit, offset = offset,
                                             keyword = keyword)

    return make_response(SUCCESS, member_list = member_list, count = count)


# @main_api.route('/download_wallet_excel', methods=['GET', 'POST'])
# def app_download_wallet_excel():
#     status, user_info = UserLogin.verify_token(request.json.get('token'))
#     if status != SUCCESS:
#         return make_response(status)
#
#     uqun_id = request.json.get('uqun_id')
#
#     excel_path = build_wallet_excel(user_info = user_info, uqun_id = uqun_id)
#
#     return send_file(excel_path)
