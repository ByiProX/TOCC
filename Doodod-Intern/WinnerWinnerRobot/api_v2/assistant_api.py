# -*- coding: utf-8 -*-
import time
import threading

from flask import request

from configs.config import main_api_v2, ANDROID_SERVER_URL_BOT_STATUS, ANDROID_SERVER_URL_SEND_MESSAGE
from core_v2.user_core import UserLogin,_get_a_balanced_bot,_get_qr_code_base64_str
from models_v2.base_model import *
from utils.z_utils import *


@main_api_v2.route('/assistant_list', methods=["POST"])
@para_check('token')
def assistant_list():
    # Check client or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        client_id = user_info.client_id
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})

    bot_list = BaseModel.fetch_all('client_bot_r', '*', BaseModel.where_dict({'client_id': client_id}))

    # If this client no bot, return one.
    if not bot_list:
        bot_info = _get_a_balanced_bot(user_info)
        bot_username = bot_info.username
        return response({'err_code':11,'qrcode':'data:image/jpg;base64,' + _get_qr_code_base64_str(bot_username)})




    bot_username_list = [i.bot_username for i in bot_list]

    """ 'bot_username': (chatroomname, memberlist ,create_time)"""
    bot_qun_r_dict = {}

    for i in bot_username_list:
        bot_qun_r_dict[i] = []
    client_qun_list = BaseModel.fetch_all('client_qun_r', '*', BaseModel.where_dict({'client_id': client_id}))

    for i in client_qun_list:
        chatroomname = i.chatroomname
        this_chatroom_info = BaseModel.fetch_one('a_chatroom', '*',
                                                 BaseModel.where_dict({'chatroomname': chatroomname}))
        if this_chatroom_info is None:
            continue
        memberlist = this_chatroom_info.memberlist.split(';')
        _bot_username_list = [v for v in bot_username_list if v in memberlist]
        # Update bot qun relation.
        for j in _bot_username_list:
            bot_qun_r_dict[j].append((chatroomname, memberlist, i.create_time))

    res = {'err_code': 0, 'content': []}
    bot_status_dict = requests.get(ANDROID_SERVER_URL_BOT_STATUS).json()
    for i in bot_list:
        bot_username = i.bot_username
        bot_info = BaseModel.fetch_one('a_contact', '*', BaseModel.where_dict({'username': bot_username}))
        signature = bot_info.signature if bot_info is not None else ''
        avatar_url = bot_info.avatar_url if bot_info is not None else ''
        nickname = bot_info.nickname if bot_info is not None else ''
        # Get bot nickname(User define).
        bot_nickname = ''
        for bot in bot_list:
            if bot_username == bot.bot_username:
                bot_nickname = bot.chatbot_default_nickname

        today_new_chatroom_count = 0
        cover_chatroom_count = 0
        cover_user_count = 0

        """ 'bot_username': (chatroomname, memberlist ,create_time)"""
        qun_info_list = bot_qun_r_dict[bot_username]
        for qun_info in qun_info_list:
            cover_chatroom_count += 1

            if int(time.time()) - int(qun_info[2]) < 86400:
                today_new_chatroom_count += 1

            cover_user_count += (len(qun_info[1]) - 1)

        temp = {
            'user_info': {
                'username': bot_username,
                'avatar_url': avatar_url,
                'nickname': nickname,
                'signature': signature,
                'bot_nickname': bot_nickname
            },
            'today_new_chatroom_count': today_new_chatroom_count,
            'cover_chatroom_count': cover_chatroom_count,
            'cover_user_count': cover_user_count,
            'status': 'normal' if bot_status_dict.get(bot_username) is True else 'danger'
        }
        res['content'].append(temp)

    return response(res)


@main_api_v2.route('/assistant_modify', methods=["POST"])
@para_check('token', 'bot_username')
def assistant_modify():
    # Check client or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        client_id = user_info.client_id
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})

    bot_nickname = request.json.get('bot_nickname')
    bot_username = request.json.get('bot_username')
    bot_signature = request.json.get('bot_signature')

    client_qun_list = BaseModel.fetch_all('client_qun_r', '*', BaseModel.where_dict({'client_id': client_id}))

    for qun in client_qun_list:
        chatroomname = qun.chatroomname
        this_chatroom = BaseModel.fetch_one('a_chatroom', '*', BaseModel.where_dict({'chatroomname': chatroomname}))
        if this_chatroom is None:
            continue
        memberlist = this_chatroom.memberlist.split(';')
        if bot_username in memberlist:
            # Modify bot_nickname
            if bot_nickname is not None:
                ubr_info = BaseModel.fetch_one('client_bot_r', '*',
                                               where_clause=BaseModel.where_dict({"client_id": client_id,
                                                                                  "bot_username": bot_username}))
                ubr_info.chatbot_default_nickname = bot_nickname
                ubr_info.save()

                msg = {'bot_username': bot_username,
                       'data': {
                           "task": "update_self_displayname",
                           "chatroomname": chatroomname,
                           "selfdisplayname": bot_nickname,
                       }}
                resp = requests.post(ANDROID_SERVER_URL_SEND_MESSAGE, json=msg)

            # Modify bot_signature.
            if bot_signature is not None:
                msg = {'bot_username': bot_username,
                       'data': {
                           "task": "update_signature",
                           "new_signature": bot_signature,
                       }}
                resp = requests.post(ANDROID_SERVER_URL_SEND_MESSAGE, json=msg)

    return response({'err_code': 0, 'content': 'success'})
