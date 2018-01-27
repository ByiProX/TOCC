# -*- coding: utf-8 -*-
import json

from flask import request

from config import app, SUCCESS
from core.user import UserLogin
from utils.u_response import make_response


@app.route('/verify_code', methods=['POST'])
def app_verify_code():
    """
    用于验证
    code: 微信传入的code
    """
    data_json = json.loads(request.data)
    code = data_json.get('code')

    user_login = UserLogin(code)
    status, token = user_login.get_user_token()

    if status == SUCCESS:
        return make_response(status, token=token)
    else:
        return make_response(status)


@app.route('/set_rebot_nickname', methods=['POST'])
def set_rebot_nickname():
    """
    用于设置rebot名字
    """
    status = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

