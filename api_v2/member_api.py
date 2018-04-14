# -*- coding: utf-8 -*-
import json

from flask import request

from configs.config import main_api_v2, SUCCESS
from core_v2.user_core import UserLogin
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
import time


@main_api_v2.route("/get_in_out_members", methods = ['POST'])
def member_get_in_out_member():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    check_time = request.json.get('date_type')
    group = request.json.get('chatroomname')
    # status = request.json.get('status')

    members = BaseModel.fetch_one("a_member", "*", where_clause=BaseModel.where_dict({"chatroomname": group})).members
    # print members[0]['username']
    for member in members:
        # print member['is_deleted']
        # if member[]
        member_info = BaseModel.fetch_one("a_contact", "*", where_clause=BaseModel.where_dict({"username": member['username']}))

        if not member['is_deleted']:
            try:
                # print member_info.create_time, member_info.update_time
                if check_time <= member_info.create_time:
                    in_list.append(member)
            except AttributeError:
                pass

        else:
            try:
                if check_time <= member_info.update_time:
                    out_list.append(member)
            except AttributeError:
                pass

    last_update_time = int(time.time())
    # 业务逻辑

    return make_response(SUCCESS, in_list = in_list, out_list = out_list, last_update_time = last_update_time)
