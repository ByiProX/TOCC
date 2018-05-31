# -*- coding: utf-8 -*-
import logging

from flask import request

from configs.config import *
from core_v2.user_core import _get_a_balanced_bot
from models_v2.base_model import BaseModel, CM
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
    # ubr = BaseModel.fetch_by_id("client_bot_r", "5ad44cb1f5d7e2658a2c175b")
    # ubr.bot_username = "wxid_l66m6wuilug912"
    # ubr.save()
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

    # username = request.json.get("username")
    # a_contact = BaseModel.fetch_one(Contact, "*", where_clause = BaseModel.where_dict({"username": username}))
    # print json.dumps(a_contact.to_json_full())
    # status, user_info = UserLogin.verify_token(request.json.get('token'))
    # if status != SUCCESS:
    #     return make_response(status)
    #
    # bot_info = _get_a_balanced_bot(user_info)
    # if bot_info:
    #     return make_response(SUCCESS, a_contact = bot_info.to_json_full())

    # uqr = CM(UserQunR)
    # uqr.client_id = 100
    # uqr.chatroomname = "716646600@chatroom"
    # uqr.status = 1
    # uqr.group_id = u"100_0"
    # uqr.create_time = datetime_to_timestamp_utc_8(datetime.now())
    # uqr.save()

    # ubr = BaseModel.fetch_by_id("client_bot_r", "5aed1e19f5d7e2638e2e6fbb")
    # ubr.bot_username = "wxid_6mf4yqgs528e22"
    # ubr.save()

    user_info_list = BaseModel.fetch_all(UserInfo, "*", BaseModel.where("!=", "username", ""))
    for user_info in user_info_list:
        ubr = BaseModel.fetch_one(UserBotR, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
        if not ubr:
            bot_info = _get_a_balanced_bot(user_info)
            ubr_info = CM(UserBotR)
            ubr_info.client_id = user_info.client_id
            ubr_info.bot_username = bot_info.username
            ubr_info.is_work = 1
            ubr_info.save()

    # client_id = request.json.get("client_id", 99)
    # ubr = BaseModel.fetch_one("client_bot_r", "*", where_clause = BaseModel.where_dict({"client_id": client_id}))
    # ubr.bot_username = "wxid_u44s9oamh0tx22"
    # ubr.save()
    # ubr = BaseModel.fetch_one("client_bot_r", "*", where_clause = BaseModel.where_dict({"client_id": 139}))
    # ubr.bot_username = "wxid_u44s9oamh0tx22"
    # ubr.save()

    return make_response(SUCCESS)


@main_api_v2.route("/exchange_bot_username", methods = ['POST'])
def exchange_bot_usrname():
    client_id = request.json.get("client_id")
    bot_username = request.json.get("bot_username")
    if not client_id or not bot_username:
        return make_response(ERR_INVALID_PARAMS)

    ubr = BaseModel.fetch_one("client_bot_r", "*", where_clause = BaseModel.where_dict({"client_id": client_id}))
    ubr.bot_username = bot_username
    ubr.save()

    return make_response(SUCCESS)


@main_api_v2.route("/get_code", methods = ['GET', 'POST'])
def get_code():
    client_id = 1
    if request.method == 'GET':
        client_id = request.args.get("client_id", 1)
    elif request.method == 'POST':
        client_id = request.json.get("client_id", 1)
    client = BaseModel.fetch_one(UserInfo, "*", where_clause = BaseModel.where_dict({"client_id": client_id}))

    return make_response(SUCCESS, client = client)
