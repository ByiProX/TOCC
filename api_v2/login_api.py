# -*- coding: utf-8 -*-
import json

from flask import request

from configs.config import api_v2, ERR_PARAM_SET, ERR_INVALID_PARAMS, SUCCESS
from core_v2.user_core import UserLogin
from utils.u_response import make_response


@api_v2.route('/verify_code', methods=['POST'])
def login_verify_code():
    """
    用于验证
    code: 微信传入的code
    {"code":"111"}
    """
    if not request.data:
        return make_response(ERR_PARAM_SET)
    data_json = json.loads(request.data)
    code = data_json.get('code')
    if not code:
        return make_response(ERR_INVALID_PARAMS)

    user_login = UserLogin(code)
    status, user_info = user_login.get_user_token()
    # TODO 这里有bug
    if status == SUCCESS:
        return make_response(status, user_info = user_info.to_dict())
    else:
        return make_response(status)