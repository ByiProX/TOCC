# -*- coding: utf-8 -*-
import json
import logging
import requests
from configs.config import ANDROID_SERVER_URL_BOT_STATUS
import json

import time
from flask import request

from configs.config import SUCCESS, main_api_v2, BotInfo, Message, NEW_MSG_Q, Contact, GLOBAL_RULES_UPDATE_FLAG, \
    GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG, GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG, \
    GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG, MaterialLib, UserInfo, UserBotR, GLOBAL_EMPLOYEE_PEOPLE_FLAG, \
    ERR_HAVE_SAME_PEOPLE, ERR_WRONG_ITEM, BOT_DEAD
from core_v2.matching_rule_core import gm_rule_dict, gm_default_rule_dict, get_gm_rule_dict, get_gm_default_rule_dict
from core_v2.message_core import route_msg, count_msg, update_sensitive_word_list, update_employee_people_list, \
    NEED_UPDATE_REPLY_RULE, update_employee_people_reply_rule
from core_v2.qun_manage_core import _bind_qun_success
from core_v2.user_core import _bind_bot_success, UserLogin
from core_v2.wechat_core import WechatConn, wechat_conn_dict
from models_v2.base_model import BaseModel, CM
from utils.u_model_json_str import verify_json
from utils.u_response import make_response

from core_v2.qun_message_check import check_is_at_bot
from unicodedata import normalize

logger = logging.getLogger('main')


@main_api_v2.route('/android/add_friend', methods=['POST'])
def android_add_friend():
    verify_json()
    user_nickname = request.json.get('user_nickname')
    user_username = request.json.get('user_username')
    bot_username = request.json.get('bot_username')
    bot = BaseModel.fetch_one(BotInfo, '*', where_clause=BaseModel.where_dict({"username": bot_username}))

    logger.info(u"发现加bot好友用户. username: %s." % user_username)
    status, user_info = _bind_bot_success(user_nickname, user_username, bot)
    if status == SUCCESS:
        if user_info.app == "yaca":
            we_conn = wechat_conn_dict.get(user_info.app)
            if we_conn is None:
                logger.info(
                    u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (
                        user_info.app, json.dumps(wechat_conn_dict.keys())))
            we_conn.send_txt_to_follower(
                "您好，欢迎使用友问币答！请将我拉入您要管理的区块链社群，拉入成功后即可为您的群提供实时查询币价，涨幅榜，币种成交榜，交易所榜，最新动态，行业百科等服务。步骤如下：\n拉我入群➡确认拉群成功➡ "
                "机器人在群发自我介绍帮助群友了解规则➡群友按照命令发关键字➡机器人回复➡完毕",
                user_info.open_id)
            # else:
            #     EmailAlert.send_ue_alert(u"有用户尝试绑定机器人，但未绑定成功.疑似网络通信问题. "
            #                              u"user_username: %s." % user_username)

    return make_response(SUCCESS)


@main_api_v2.route('/android/add_friend_by_force', methods=['POST'])
def android_add_friend_by_force():
    verify_json()
    user_nickname = request.json.get('user_nickname')
    user_username = request.json.get('user_username')
    bot_username = request.json.get('bot_username')

    logger.info(u"发现加 bot 好友用户. username: %s." % user_username)
    user_info_list = CM(UserInfo).fetch_all(UserInfo, '*', where_clause = BaseModel.where_dict({"nick_name": user_nickname}))
    if len(user_info_list) > 1:
        logger.error(u"发现多个 nickname: %s. bot_username: %s. user_username: %s. client_id_list: %s." % (user_nickname, bot_username, user_username, json.dumps([r.client_id for r in user_info_list])))
        return ERR_HAVE_SAME_PEOPLE, None
    elif len(user_info_list) == 0:
        logger.error(u"未找到 nickname: %s. bot_username: %s. user_username: %s" % (user_nickname, bot_username, user_username))
        return ERR_WRONG_ITEM, None

    user_info = user_info_list[0]
    user_info.username = user_username
    user_info.save()
    logger.info(u"username 绑定成功")

    ubr_info = BaseModel.fetch_one(UserBotR, '*', where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                       "bot_username": bot_username}))
    if not ubr_info:
        ubr_info = CM(UserBotR)
        ubr_info.client_id = user_info.client_id
        ubr_info.is_work = 1

    ubr_info.bot_username = bot_username
    ubr_info.save()
    logger.info(u"ubr 绑定成功")

    return make_response(SUCCESS)


@main_api_v2.route('/android/add_qun', methods=['POST'])
def android_add_qun():
    print ">>>>>>>>>>>>>>>>>>>我要开始建群啦啦啦啦啦"
    verify_json()
    # user_nickname = request.json.get('user_nickname')
    user_username = request.json.get('user_username')
    bot_username = request.json.get('bot_username')
    chatroomname = request.json.get("chatroomname")

    status, user_info_list = _bind_qun_success(chatroomname, "", bot_username, user_username)

    return make_response(SUCCESS)


@main_api_v2.route('/android/add_material', methods=['POST'])
def android_add_material():
    verify_json()
    username = request.json.get('username')
    bot_username = request.json.get('bot_username')
    user_info_list = BaseModel.fetch_all(UserInfo, "*", where_clause=BaseModel.where_dict({"username": username}))
    for user_info in user_info_list:
        ubr = BaseModel.fetch_one(UserBotR, "*", where_clause=BaseModel.where_dict({"bot_username": bot_username,
                                                                                    "client_id": user_info.client_id}))
        if ubr:
            material_lib = CM(MaterialLib).from_json(request.json)
            material_lib.client_id = user_info.client_id
            material_lib.save()

    return make_response(SUCCESS)


@main_api_v2.route("/android/new_message", methods=['POST'])
def android_new_message():
    verify_json()
    a_message = CM(Message).from_json(request.json)
    a_message.set_id(request.json.get('a_message_id'))

    '''
    req = requests.get(ANDROID_SERVER_URL_BOT_STATUS)
    client_bots_alive = json.loads(req.content)

    # 判断主副机器人的存活状态
    client_qun_r = BaseModel.fetch_one("client_qun_r", "*",
                                       where_clause=BaseModel.and_(
                                           ["=", "chatroomname", a_message.talker]
                                       ))

    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>."
    print client_qun_r
    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    client_id = client_qun_r.client_id

    client_bot_r = BaseModel.fetch_one("client_bot_r", "*",
                                       where_clause=BaseModel.and_(
                                           ["=", "client_id", client_id]
                                       ))

    host_bot = client_bot_r.bot_username
    standby_bots_list = [standby_bot['bot_username'] for standby_bot in client_bot_r.standby_bots]
    bot_who_catch_msg = a_message.bot_username

    # 如果该消息是主机器人收集到
    if bot_who_catch_msg == host_bot:
        if not client_bots_alive[bot_who_catch_msg]:
            return make_response(BOT_DEAD)

    # 如果该消息是备用机器人收集到
    elif bot_who_catch_msg in standby_bots_list:
        # 如果备用机器人活着
        if client_bots_alive[host_bot]:
            return make_response(SUCCESS)
    '''
    ################################

    global gm_rule_dict
    global gm_default_rule_dict
    global NEED_UPDATE_REPLY_RULE

    if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG]:
        gm_rule_dict = get_gm_rule_dict()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = False
    if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG]:
        gm_default_rule_dict = get_gm_default_rule_dict()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG] = False
    if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG]:
        update_sensitive_word_list()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG] = False
    if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_EMPLOYEE_PEOPLE_FLAG]:
        update_employee_people_list()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_EMPLOYEE_PEOPLE_FLAG] = False
    if NEED_UPDATE_REPLY_RULE:
        update_employee_people_reply_rule()
        NEED_UPDATE_REPLY_RULE = False
    route_msg(a_message, gm_rule_dict, gm_default_rule_dict)
    count_msg(a_message)
    try:
        check_is_at_bot(a_message)
    except Exception:
        pass
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

    return make_response(SUCCESS, bot_info=bot_info.to_json_full())


@main_api_v2.route("/android/get_bot_list", methods=['POST'])
def android_get_bot_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    bot_list = list()

    ubr_list = BaseModel.fetch_all("client_bot_r", "*")
    for ubr in ubr_list:
        bot_info = BaseModel.fetch_one(BotInfo, "*", where_clause=BaseModel.where_dict({"username": ubr.bot_username}))
        a_contact_bot = BaseModel.fetch_one(Contact, "*",
                                            where_clause=BaseModel.where_dict({"username": ubr.bot_username}))
        if not bot_info:
            continue
        bot_info_json = bot_info.to_json_full()
        if not a_contact_bot:
            a_contact_bot = CM(a_contact_bot)
        bot_info_json.update(a_contact_bot.to_json_full())
        bot_list.append(bot_info_json)

    return make_response(SUCCESS, bot_info_list=bot_list)
