# -*- coding: utf-8 -*-
import json
import logging

from models_v2.base_model import BaseModel

logger = logging.getLogger('main')


if __name__ == '__main__':
    BaseModel.extract_from_json()
    a_chatroom_r_list = BaseModel.fetch_all("a_chatroom_r", "*" , where_clause = BaseModel.where_dict({"bot_username": "wxid_eg8kqg9ajk4d22"}))
    chatroomname_list = [r.chatroomname for r in a_chatroom_r_list]
    print 'chatroomname_list', json.dumps(chatroomname_list)
    user_username_set = {"EvaZhu1990", "wxid_094ows6qxz3712", "wxid_4sg3zyxf8r6912", "wxid_fibbgpc2i6y012", "EvaZhu2016", "L1381009z", "wxid_otjpj5h5qzxe22", "yangshuhang1112", "wxid_z42ns41xxcms12", "Su_031118", "shangcengkefu", "yxn568696", "wxid_vr5olegcnqlp22", "sczspg001", "wxid_pf9j80ehs3mm12", "wxid_fncpiwa7o3gm12", "pinguan-heyinyan"}


pass
