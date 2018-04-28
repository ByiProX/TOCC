# -*- coding: utf-8 -*-

import logging

import time
from flask import request

from configs.config import main_api_v2, SUCCESS, UserInfo
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
    ubr = BaseModel.fetch_one("client_bot_r", "5ae446d7f5d7e26c380d2324")
    ubr.bot_username = "wxid_lkruzsl7w2r822"
    ubr.save()
    return make_response(SUCCESS)
