# -*- coding: utf-8 -*-
import json
import logging

import time
from flask import request

from configs.config import SUCCESS, main_api_v2, BotInfo, Message, NEW_MSG_Q, Contact, GLOBAL_RULES_UPDATE_FLAG, \
    GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG, GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG, \
    GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG
from core_v2.matching_rule_core import gm_rule_dict, gm_default_rule_dict, get_gm_rule_dict, get_gm_default_rule_dict
from core_v2.message_core import route_msg, count_msg, update_sensitive_word_list
from core_v2.user_core import _bind_bot_success, UserLogin
from core_v2.wechat_core import WechatConn, wechat_conn_dict
from models_v2.base_model import BaseModel, CM
from utils.u_model_json_str import verify_json
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api_v2.route('/android/add_friend', methods=['POST'])
def android_add_friend():
    verify_json()
    user_nickname = request.json.get('user_nickname')
    user_username = request.json.get('user_username')
    bot_username = request.json.get('bot_username')
    bot = BaseModel.fetch_one(BotInfo, '*', where_clause = BaseModel.where_dict({"username": bot_username}))

    logger.info(u"发现加bot好友用户. username: %s." % user_username)
    status, user_info = _bind_bot_success(user_nickname, user_username, bot)
    if status == SUCCESS:
        if user_info.app == "yaca":
            we_conn = wechat_conn_dict.get(user_info.app)
            if we_conn is None:
                logger.info(
                    u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (user_info.app, json.dumps(wechat_conn_dict.keys())))
            we_conn.send_txt_to_follower(
                "您好，欢迎使用数字货币友问币答！请将我拉入您要管理的区块链社群，拉入成功后即可为您的群提供实时查询币价，涨幅榜，币种成交榜，交易所榜，最新动态，行业百科等服务。步骤如下：\n拉我入群➡确认拉群成功➡ "
                "机器人在群发自我介绍帮助群友了解规则➡群友按照命令发关键字➡机器人回复➡完毕",
                user_info.open_id)
            # else:
            #     EmailAlert.send_ue_alert(u"有用户尝试绑定机器人，但未绑定成功.疑似网络通信问题. "
            #                              u"user_username: %s." % user_username)

    return make_response(SUCCESS)


@main_api_v2.route("/android/new_message", methods=['POST'])
def android_new_message():
    verify_json()
    a_message = CM(Message).from_json(request.json)
    a_message.set_id(request.json.get('a_message_id'))
    a_message.create_time = int(a_message.create_time / 1000)

    global gm_rule_dict
    global gm_default_rule_dict

    if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG]:
        gm_rule_dict = get_gm_rule_dict()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = False
    if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG]:
        gm_default_rule_dict = get_gm_default_rule_dict()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG] = False
    if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG]:
        update_sensitive_word_list()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG] = False
    route_msg(a_message, gm_rule_dict, gm_default_rule_dict)
    count_msg(a_message)
    # NEW_MSG_Q.put(a_message)
    # logger.info(u"NEW_MSG_Q.put(a_message)")
    # route_msg(a_message)
    # count_msg(a_message)
    return make_response(SUCCESS)


@main_api_v2.route("/android/add_bot", methods=['GET', 'POST'])
def init_bot_info():
    if request.method == 'POST':
        username = request.json.get('username')
    else:
        username = request.args.get("username")
    bot_info = CM("bot_info")
    bot_info.username = username
    bot_info.create_bot_time = int(time.time())
    bot_info.alive_detect_time = int(time.time())
    bot_info.is_alive = 1
    bot_info.save()

    return make_response(SUCCESS, bot_info = bot_info.to_json_full())


@main_api_v2.route("/android/get_bot_list", methods=['POST'])
def android_get_bot_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    bot_list = list()

    ubr_list = BaseModel.fetch_all("client_bot_r", "*")
    for ubr in ubr_list:
        bot_info = BaseModel.fetch_one(BotInfo, "*", where_clause = BaseModel.where_dict({"username": ubr.bot_username}))
        a_contact_bot = BaseModel.fetch_one(Contact, "*", where_clause = BaseModel.where_dict({"username": ubr.bot_username}))
        if not bot_info:
            continue
        bot_info_json = bot_info.to_json_full()
        if not a_contact_bot:
            a_contact_bot = CM(a_contact_bot)
        bot_info_json.update(a_contact_bot.to_json_full())
        bot_list.append(bot_info_json)

    return make_response(SUCCESS, bot_info_list = bot_list)
