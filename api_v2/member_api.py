# -*- coding: utf-8 -*-
import json

from flask import request

from configs.config import main_api_v2, SUCCESS, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from models_v2.base_model import BaseModel
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
import time


#####################

@main_api_v2.route("/get_in_out_members", methods=['POST'])
def member_get_in_out_member():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()-time.time()%86400-86400*6))

    cur_time = time.time()
    today_start = int(cur_time - cur_time % 86400)
    yesterday_start = int(cur_time - cur_time % 86400 - 86400)
    seven_before = int(cur_time - cur_time % 86400 - 86400 * 6)
    thirty_before = int(cur_time - cur_time % 86400 - 86400 * 29)

    time_dict = {
        1: today_start,
        2: yesterday_start,
        3: seven_before,
        4: thirty_before,
        5: 0
    }

    date_type = request.json.get('date_type')
    if date_type is None:
        return make_response(ERR_WRONG_ITEM)
    check_time = time_dict[date_type]
    group = request.json.get('chatroomname')

    in_list = list()
    out_list = list()

    # a_member = BaseModel.fetch_one("a_member", "*", where_clause=BaseModel.where_dict({"chatroomname": group}))
    a_member = BaseModel.fetch_all("a_member", "*", where_clause=BaseModel.where_dict({"chatroomname": group}))[0]

    if not a_member:
        pass
        # return make_response(ERR_WRONG_ITEM)
    else:
        members = a_member.members
        for member in members:
            member_info = BaseModel.fetch_all("a_contact",
                                              ["username", "avatar_url", "nickname", "id", "img_lastupdatetime"],
                                              # "*",
                                              where_clause=BaseModel.where_dict({"username": member.get('username')}))[0]

            if not member['is_deleted']:
                try:
                    if check_time <= member.get("create_time"):
                        member.update(member_info.to_json_full())
                        in_list.append(member)
                except AttributeError:
                    pass

            else:
                try:
                    if check_time <= member.get("update_time"):
                        member.update(member_info.to_json_full())
                        out_list.append(member)
                except AttributeError:
                    pass

    last_update_time = int(time.time())
    print ":::::::::::::::::::::::::::::::::::::::::::::"
    print in_list

    return make_response(SUCCESS, in_list=in_list, out_list=out_list, last_update_time=last_update_time)
