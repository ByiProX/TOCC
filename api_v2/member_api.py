# -*- coding: utf-8 -*-
import json

from flask import request

from configs.config import main_api_v2, SUCCESS
from core_v2.user_core import UserLogin
from utils.u_model_json_str import verify_json
from utils.u_response import make_response


@main_api_v2.route("/get_in_out_members", methods = ['POST'])
def member_get_in_out_member():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    in_list = list()
    out_list = list()

    # 业务逻辑

    return make_response(SUCCESS, in_list = in_list, out_list = out_list)
