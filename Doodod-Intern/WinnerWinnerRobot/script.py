# -*- coding: utf-8 -*-
import json
import logging

from models_v2.base_model import BaseModel

logger = logging.getLogger('main')


if __name__ == '__main__':
    BaseModel.extract_from_json()
    # a_chatroom_r_list = BaseModel.fetch_all("a_chatroom_r", "*" , where_clause = BaseModel.where_dict({"bot_username": "wxid_eg8kqg9ajk4d22"}))
    # chatroomname_list = [r.chatroomname for r in a_chatroom_r_list]
    # print 'chatroomname_list', json.dumps(chatroomname_list)
    # user_username_set = {"EvaZhu1990", "wxid_094ows6qxz3712", "wxid_4sg3zyxf8r6912", "wxid_fibbgpc2i6y012", "EvaZhu2016", "L1381009z", "wxid_otjpj5h5qzxe22", "yangshuhang1112", "wxid_z42ns41xxcms12", "Su_031118", "shangcengkefu", "yxn568696", "wxid_vr5olegcnqlp22", "sczspg001", "wxid_pf9j80ehs3mm12", "wxid_fncpiwa7o3gm12", "pinguan-heyinyan"}
    # client_bot_r = BaseModel.fetch_all("client_bot_r", "*", where_clause = BaseModel.where_dict({"bot_username": "wxid_eg8kqg9ajk4d22"}))
    # client_bot_r_id = [r.client_id for r in client_bot_r]
    # print 'client_bot_r_id', json.dumps(client_bot_r_id)
    # for client_id in client_bot_r_id:
    #     user_info = BaseModel.fetch_one("client_member", "*", where_clause = BaseModel.where_dict({"client_id": client_id}))
    #     print 'client nick_name', user_info.nick_name

    # user_info_list = BaseModel.fetch_all("client_member", "*", where_clause = BaseModel.where_dict(["like", "nick_name", "客服"]))
    # for user_info in user_info_list:
    #     ubr = BaseModel.fetch_one("client_bot_r", "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    #     if ubr:
    #         print user_info.client_id, user_info.nick_name, user_info.username, ubr.bot_username
    #     else:
    #         print 'no ubr', user_info.client_id, user_info.nick_name, user_info.username

    user_info = BaseModel.fetch_one("client_member", "*", where_clause = BaseModel.where_dict(["like", "nick_name", ""]))
    if user_info:
        print user_info.client_id, user_info.username
        ubr = BaseModel.fetch_one("client_bot_r", "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
        if ubr:
            print ubr.bot_username
            ubr.bot_username = "wxid_ljpr5royfums21"
            # ubr.save()


pass
