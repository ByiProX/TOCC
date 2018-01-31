# -*- coding: utf-8 -*-
import logging

from datetime import datetime, timedelta

import models
import api
from config import db
from core.user import UserLogin
from models.user_bot import UserBotRelateInfo, UserInfo, BotInfo

models.import_str = ""
api.api_str = ""

logger = logging.getLogger('main')


def create_all_databases():
    db.drop_all()
    db.create_all()


def add_wechat_bot_info(b_info=None):
    """
    用户新增
    :return:
    """
    if b_info and isinstance(b_info, UserBotRelateInfo):
        db.session.add(b_info)
    else:
        ubr_info = UserBotRelateInfo()
    db.session.commit()


# 测试使用
def initial_some_user_info():
    user_info_1 = UserInfo()
    user_info_1.open_id = "test_open_id_1"
    user_info_1.union_id = "test_union_id_1"
    user_info_1.nick_name = "测试账号"
    user_info_1.sex = 1
    user_info_1.province = '北京'
    user_info_1.city = '东城区'
    user_info_1.country = '中国'
    user_info_1.avatar_url = 'http:'

    user_info_1.code = "sfvgkjvsgrkn"
    user_info_1.create_time = datetime.now()

    user_info_1.last_login_time = datetime.now()
    user_info_1.token = 'test_token_123'
    user_info_1.token_expired_time = datetime.now() + timedelta(days=5)

    user_info_1.func_send_qun_messages = False
    user_info_1.func_qun_sign = False
    user_info_1.func_auto_reply = False
    user_info_1.func_welcome_message = False

    user_info_2 = UserInfo()
    user_info_2.open_id = "test_open_id_2"
    user_info_2.union_id = "test_union_id_2"
    user_info_2.nick_name = "测试账号2"
    user_info_2.sex = 1
    user_info_2.province = '天津'
    user_info_2.city = '某区'
    user_info_2.country = '中国'
    user_info_2.avatar_url = 'http:'

    user_info_2.code = "sfhsfbh"
    user_info_2.create_time = datetime.now()

    user_info_2.last_login_time = datetime.now()
    user_info_2.token = 'test_token_345'
    user_info_2.token_expired_time = datetime.now() + timedelta(days=5)

    user_info_2.func_send_qun_messages = False
    user_info_2.func_qun_sign = False
    user_info_2.func_auto_reply = False
    user_info_2.func_welcome_message = False

    db.session.add(user_info_1)
    db.session.add(user_info_2)
    db.session.commit()


def initial_some_bot_info():
    bot_info_1 = BotInfo()
    bot_info_1.username = "test_android_username"
    bot_info_1.create_bot_time = datetime.now()
    bot_info_1.is_alive = True
    bot_info_1.alive_detect_time = datetime.now()

    bot_info_2 = BotInfo()
    bot_info_2.username = "test_android_username_2"
    bot_info_2.create_bot_time = datetime.now()
    bot_info_2.is_alive = True
    bot_info_2.alive_detect_time = datetime.now()

    bot_info_3 = BotInfo()
    bot_info_3.username = "test_android_username_3"
    bot_info_3.create_bot_time = datetime.now()
    bot_info_3.is_alive = False
    bot_info_3.alive_detect_time = datetime.now()

    db.session.add(bot_info_1)
    db.session.add(bot_info_2)
    db.session.add(bot_info_3)
    db.session.commit()
