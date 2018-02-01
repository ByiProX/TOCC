# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from models.android_db import ABot
from models.qun_friend import GroupInfo, UserQunRelateInfo, UserQunBotRealteInfo
from models.user_bot import UserInfo, BotInfo


def get_a_default_test_user_info():
    user_info_1 = UserInfo()
    user_info_1.open_id = "test_open_id_1_afksb"
    user_info_1.union_id = "test_union_id_1_afksb"
    user_info_1.username = ''
    user_info_1.nick_name = "测试账号_afksb"
    user_info_1.sex = 1
    user_info_1.province = '北京'
    user_info_1.city = '东城区'
    user_info_1.country = '中国'
    user_info_1.avatar_url = 'http:'

    user_info_1.code = "hasgafksb"
    user_info_1.create_time = datetime.now()

    user_info_1.last_login_time = datetime.now()
    user_info_1.token = 'fadlhuarnwk'
    user_info_1.token_expired_time = datetime.now() + timedelta(days=5)

    user_info_1.func_send_qun_messages = False
    user_info_1.func_qun_sign = False
    user_info_1.func_auto_reply = False
    user_info_1.func_welcome_message = False
    return user_info_1


def get_a_default_test_bot_info():
    bot_info_1 = BotInfo()
    bot_info_1.username = 'test_bot_username'
    bot_info_1.create_bot_time = datetime.now()
    bot_info_1.is_alive = True
    bot_info_1.alive_detect_time = datetime.now()
    bot_info_1.qr_code = 'http:'
    return bot_info_1


def get_a_default_test_a_bot():
    a_bot_1 = ABot()
    a_bot_1.username = 'test_bot_username'
    a_bot_1.type = -999
    a_bot_1.avatar_url2 = 'http:'
    a_bot_1.create_time = datetime.now()
    a_bot_1.update_time = datetime.now()
    return a_bot_1


def get_a_default_test_group_info(user_id):
    group_info_1 = GroupInfo()
    group_info_1.user_id = user_id
    group_info_1.group_nickname = '测试分组用'
    group_info_1.create_time = datetime.now()
    group_info_1.is_default = False

    return group_info_1


def get_a_default_test_uqr_info(user_id, group_id):
    uqr_info = UserQunRelateInfo()
    uqr_info.user_id = user_id
    uqr_info.chatroomname = 'test_chatroomname_wihurt'
    uqr_info.group_id = group_id
    uqr_info.create_time = datetime.now()
    uqr_info.is_deleted = False

    return uqr_info


def get_a_default_test_uqbr_info(user_bot_id):
    uqbr_info = UserQunBotRealteInfo()
    uqbr_info.user_bot_rid = user_bot_id
    uqbr_info.is_error = False

    return uqbr_info


def get_a_default_cur_info():
    raise NotImplementedError
