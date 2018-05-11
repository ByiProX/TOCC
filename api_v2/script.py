# -*- coding: utf-8 -*-
import json
import logging

import time
from flask import request

from configs.config import main_api_v2, SUCCESS, UserInfo, MaterialLib, Message
from core_v2.send_msg import send_ws_to_android
from crawler.coin_all_crawler_v2 import update_coin_all
from models_v2.base_model import BaseModel
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api_v2.route("/script", methods = ['GET', 'POST'])
def script():
    # uqr = BaseModel.fetch_by_id("client_qun_r", "5ad46153f5d7e26589658ba7")
    # uqr.group_id = u"4_0"
    # uqr.update()
    # user_info_list = BaseModel.fetch_all("client_member", "*")
    # for user_info in user_info_list:
    #     user_info.app = "yaca"
    #     user_info.save()
    # user_info = BaseModel.fetch_one(UserInfo, "*", where_clause = BaseModel.where_dict({"client_id": 15}))
    # user_info.username = u"ada390859"
    # user_info.save()
    # update_coin_all()
    ubr = BaseModel.fetch_by_id("client_bot_r", "5ad44cb1f5d7e2658a2c175b")
    ubr.bot_username = "wxid_q05k9d2atjie22"
    ubr.save()
    #
    # material_list = BaseModel.fetch_all(MaterialLib, "*")
    # for material in material_list:
    #     msg_id = material.msg_id
    #     msg = BaseModel.fetch_one(Message, "*", where_clause = BaseModel.where_dict({"msg_id": msg_id}))
    #     print json.dumps(msg.to_json_full())

    # bot_username = "wxid_l66m6wuilug912"
    # data = {"chatroomname": "4893318868@chatroom",
    #         "task": "update_chatroom"}
    # send_ws_to_android(bot_username, data)

    return make_response(SUCCESS)
