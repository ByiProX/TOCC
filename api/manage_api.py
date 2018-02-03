# -*- coding: utf-8 -*-
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api, ERR_SET_LENGTH_WRONG
from core.qun_manage_core import create_new_group, get_group_list, rename_a_group, delete_a_group
from core.user_core import UserLogin
from utils.u_response import make_response


@main_api.route('/add_group', methods=['POST'])
def app_add_a_group():
    """
    为一个用户新增一个组
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    new_group_name = request.json.get('new_group_name')
    if len(new_group_name) < 1 or len(new_group_name) > 16:
        return make_response(ERR_SET_LENGTH_WRONG)

    if not new_group_name:
        return make_response(ERR_PARAM_SET)

    status, group = create_new_group(group_name=new_group_name, user_id=user_info.user_id)

    if status == SUCCESS:
        return make_response(status, group=group)
    else:
        return make_response(status)


@main_api.route('/get_group_list', methods=['POST'])
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


@main_api.route('/rename_a_group', methods=['POST'])
def app_rename_a_group():
    """
    将一个已有分组改名
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    new_group_name = request.json.get('new_group_name')
    if len(new_group_name) < 1 or len(new_group_name) > 16:
        return make_response(ERR_SET_LENGTH_WRONG)
    group_id = request.json.get('group_id')

    status = rename_a_group(new_group_name, group_id, user_info.user_id)

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


@main_api.route('/delete_a_group', methods=['POST'])
def app_delete_a_group():
    """
    删除一个分组
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    group_id = request.json.get('group_id')

    status = delete_a_group(group_id, user_info.user_id)

    if status == SUCCESS:
        return make_response(SUCCESS)
    else:
        return make_response(status)


def app_transfor_qun_into_group():
    """
    将一个群从一个群里面移动到另一个群里面
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    raise NotImplementedError
