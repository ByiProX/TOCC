# -*- coding: utf-8 -*-

from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
from core.user_core import UserLogin
from utils.u_response import make_response


@main_api.route('/get_material_list', methods=['POST'])
def app_get_material_list():
    """
    读取该用户的某种资源
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    material_type = request.json.get('material_type')
    if not material_type:
        return make_response(ERR_PARAM_SET)

    raise NotImplementedError
