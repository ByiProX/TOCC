# -*- coding: utf-8 -*-
import json
import logging

import time
from flask import request

from configs.config import SUCCESS, main_api_v2, BotInfo, Message, NEW_MSG_Q, Contact, GLOBAL_RULES_UPDATE_FLAG, \
    GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG, GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG, \
    GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG, MaterialLib, UserInfo, UserBotR, GLOBAL_EMPLOYEE_PEOPLE_FLAG
from core_v2.matching_rule_core import gm_rule_dict, gm_default_rule_dict, get_gm_rule_dict, get_gm_default_rule_dict
from core_v2.message_core import route_msg, count_msg, update_sensitive_word_list, update_employee_people_list, \
    NEED_UPDATE_REPLY_RULE, update_employee_people_reply_rule
from core_v2.user_core import _bind_bot_success, UserLogin
from core_v2.wechat_core import WechatConn, wechat_conn_dict
from models_v2.base_model import BaseModel, CM
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from core_v2.send_msg import send_ws_to_android

from core_v2.qun_message_check import check_is_at_bot
from share_task_api import api_upload_oss, allowed_file, secure_filename
from unicodedata import normalize
from utils.u_upload_oss import put_file_to_oss

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

@main_api_v2.route("/android/modify_bot_nickname", methods=['POST'])
def modify_bot_nickname():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)
    
    bot_username = request.json.get('bot_username')
    new_nickname = request.json.get('new_nickname')
    data = {
        "task": "update_nickname",
        "new_nickname": new_nickname
    }
    try:
        status = send_ws_to_android(bot_username, data)
        if status == SUCCESS:
            logger.info(u"更改%s名字成功, 新名字为: %s." % (bot_username, new_nickname))
        else:
            logger.info(u"更改%s名字失败." % bot_username)
    except Exception:
        pass
    return make_response(status)

@main_api_v2.route("/android/modify_bot_avatar", methods=['POST'])
def modify_bot_avatar():
    status, user_info = UserLogin.verify_token(request.form.get('token'))
    if status != SUCCESS:
        return make_response(status)

    upload_file = request.files['file']
    logger.info('upload filename: ' + upload_file.filename)
    if not upload_file or not allowed_file(upload_file.filename):
        return make_response(ERR_NOT_ALLOWED_EXTENSION)

    filename = str(user_info.client_id) + '_' + secure_filename(normalize('NFKD', upload_file.filename).encode('utf-8', 'ignore').decode('utf-8'))
    oss_url = put_file_to_oss(filename, data = upload_file.stream._file)

    bot_username = request.form.get('bot_username')
    logger.info("头像url为%s"%oss_url)
    data = {
        "task": "update_avatar",
        "new_avatar_url": oss_url,
        "filename": oss_url.split('/')[-1]
    }
    try:
        status = send_ws_to_android(bot_username, data)
        if status == SUCCESS:
            logger.info(u"更改%s头像成功." % bot_username)
        else:
            logger.info(u"更改%s头像失败." % bot_username)
    except Exception:
        pass
    return make_response(status, oss_url = oss_url)