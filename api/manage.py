# -*- coding: utf-8 -*-
from flask import request

from config import SUCCESS, ERR_PARAM_SET, main_api
from core.qun_manage import create_new_group
from core.user import UserLogin
from utils.u_response import make_response


@main_api.route('/add_a_group', methods=['POST'])
def add_a_group():
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
