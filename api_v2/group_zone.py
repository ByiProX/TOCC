# -*- coding: utf-8 -*-
from flask import request
from configs.config import main_api_v2, SUCCESS, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from models_v2.base_model import BaseModel
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
import time

MSG_TYPE_UNKNOWN = -1  # 未知类型
MSG_TYPE_TXT = 1
MSG_TYPE_PIC = 3
MSG_TYPE_MP3 = 34
MSG_TYPE_NAME_CARD = 42
MSG_TYPE_MP4 = 43
MSG_TYPE_GIF = 47
MSG_TYPE_VIDEO = 62
MSG_TYPE_SHARE = 49
MSG_TYPE_SYS = 10000
MSG_TYPE_ENTERCHATROOM = 570425393

MSG_TYPE_DICT = {
    1:

}


@main_api_v2.route("/group_zone_lists", methods=['POST'])
def get_group_zone_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    try:
        client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                          where_clause=BaseModel.where_dict({"client_id": client_id}))
        client_quns = [client_qun.to_json_full() for client_qun in client_quns]

    except:
        return make_response(ERR_WRONG_ITEM)

    try:
        for client_qun in client_quns:
            chatroom_info = BaseModel.fetch_one("a_chatroom", "*",
                                                where_clause=BaseModel.where_dict({"chatroomname": client_qun.get('chatroomname')}))


            # client_qun_to_dict = client_qun.to_json_full()
            client_qun.update(chatroom_info.to_json_full())

            # client_qun.nickname_real = chatroom_info.nickname_real if chatroom_info.nickname_real else None
            # client_qun.member_count = chatroom_info.member_count
    except:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS, client_quns_list=client_quns)


@main_api_v2.route("/group_zone_sources", methods=['POST'])
def get_group_zone_sources():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    talker = request.json.get('talker')
    keyword = request.json.get('keyword')
    source_type = request.json.get('source_type')
    page = request.json.get('page')
    pagesize = request.json.get('pagesize')


    messages = BaseModel.fetch_all('a_message', '*', _where, page = page, pagesize = pagesize, orderBy = order, group = group_by)



