# -*- coding: utf-8 -*-
from flask import request

from config import SUCCESS, ERR_PARAM_SET, main_api
from core.qun_manage import create_new_group
from core.user import UserLogin
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

    if not new_group_name:
        return make_response(ERR_PARAM_SET)

    status = create_new_group(group_name=new_group_name, user_id=user_info.user_id)

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

#TODO get_group_list 得到一个对象
# group_list是一个数组，里面是一个一个的对象group_id,group_nickname,group_chatroom_list,
# chatroom_list,里面是一个一个对象(chatroom_id,chatroom_nickname,chatroom_member_count,chatroom_status)

# transfer_chatroom,chatroom_id，target_group_id，回来给你一个success

# TODO remove