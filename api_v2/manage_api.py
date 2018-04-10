# -*- coding: utf-8 -*-
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api_v2, ERR_SET_LENGTH_WRONG, ERR_INVALID_PARAMS
from core_v2.qun_manage_core import create_new_group, get_group_list, rename_a_group, delete_a_group, \
    transfer_qun_into_a_group
from core_v2.user_core import UserLogin
from utils.u_response import make_response


@main_api_v2.route('/add_group', methods=['POST'])
def app_add_a_group():
    """
    为一个用户新增一个组
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    new_group_name = request.json.get('new_group_name')
    if not new_group_name:
        return make_response(ERR_INVALID_PARAMS)
    if len(new_group_name) < 1 or len(new_group_name) > 16:
        return make_response(ERR_SET_LENGTH_WRONG)

    if not new_group_name:
        return make_response(ERR_PARAM_SET)

    status, group = create_new_group(group_name=new_group_name, client_id=user_info.client_id)

    if status == SUCCESS:
        return make_response(status, group=group)
    else:
        return make_response(status)


@main_api_v2.route('/get_group_list', methods=['POST'])
def app_get_group_list():
    """
    根据一个用户得到一个组信息
    :return:
    """

    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    status, res = get_group_list(user_info)

    if status == SUCCESS:
        return make_response(status, group_list=res)
    else:
        return make_response(status)


@main_api_v2.route('/rename_a_group', methods=['POST'])
def app_rename_a_group():
    """
    将一个已有分组改名
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    new_group_name = request.json.get('new_group_name')
    if not new_group_name:
        return make_response(ERR_INVALID_PARAMS)
    if len(new_group_name) < 1 or len(new_group_name) > 16:
        return make_response(ERR_SET_LENGTH_WRONG)

    group_id = request.json.get('group_id')
    if not group_id:
        return make_response(ERR_INVALID_PARAMS)
    if group_id == new_group_name:
        status = SUCCESS
    else:
        status = rename_a_group(new_group_name, group_id, user_info.client_id)

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api_v2.route('/delete_a_group', methods=['POST'])
def app_delete_a_group():
    """
    删除一个分组
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    group_id = request.json.get('group_id')
    if not group_id:
        return make_response(ERR_INVALID_PARAMS)

    status = delete_a_group(group_id, user_info.client_id)

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api_v2.route('/transfer_chatroom_into_group', methods=['POST'])
def app_transfer_qun_into_group():
    """
    将一个群从一个组里面移动到另一个群里面
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    chatroomname = request.json.get('chatroomname')
    if not chatroomname:
        return make_response(ERR_INVALID_PARAMS)

    old_group_id = request.json.get('old_group_id')
    new_group_id = request.json.get('new_group_id')
    if not new_group_id or not old_group_id:
        return make_response(ERR_INVALID_PARAMS)

    status = transfer_qun_into_a_group(old_group_id, new_group_id, chatroomname, user_info.client_id)

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)
