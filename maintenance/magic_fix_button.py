# -*- coding: utf-8 -*-

import logging

from datetime import datetime

from configs.config import db
from core.qun_manage_core import set_default_group
from models.android_db_models import AContact, AFriend
from models.user_bot_models import UserInfo, BotInfo, UserBotRelateInfo

logger = logging.getLogger('main')


def set_a_user_and_bind_bot(user_id, bot_id):
    """
    将一个用户设置成和机器人绑定的状态
    """
    user_info = db.session.query(UserInfo).filter(UserInfo.user_id == user_id).first()
    if not user_info:
        raise ValueError("找不到该用户")
    bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == bot_id).first()
    if not bot_info:
        raise ValueError("找不到机器人")

    a_contact_list = db.session.query(AContact).filter(AContact.nickname == user_info.nick_name).all()
    if not a_contact_list:
        logger.error("目前bot中没有该昵称的好友")
        return -1
    true_friend_list = []
    for a_contact in a_contact_list:
        if a_contact.type % 2 == 1:
            true_friend_list.append(a_contact)
    if not true_friend_list:
        logger.error("目前有同名的人，但没有人是奇数好友")
        return -2
    if len(true_friend_list) > 1:
        logger.error("有多个人叫这个名字且是好友，无法确认关系")
        return -3

    a_contact = true_friend_list[0]
    user_username = a_contact.username

    a_friend = db.session.query(AFriend).filter(AFriend.from_username == bot_info.username,
                                                AFriend.to_username == user_username).first()

    if not a_friend:
        logger.error("双方并没有好友关系")
        return -4

    user_info.username = user_username
    db.session.merge(user_info)
    db.session.commit()

    ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_info.user_id,
                                                          UserBotRelateInfo.bot_id == bot_info.bot_id).first()

    if ubr_info:
        ubr_info.is_setted = True
        ubr_info.is_being_used = True
        db.session.merge(ubr_info)
        db.session.commit()
    else:
        ubr_info_2 = UserBotRelateInfo()
        ubr_info_2.user_id = user_info.user_id
        ubr_info_2.bot_id = bot_info.bot_id

        ubr_info_2.chatbot_default_nickname = "啊机器猫"
        ubr_info_2.preset_time = datetime.now()
        ubr_info_2.set_time = 0
        ubr_info_2.is_setted = True
        ubr_info_2.is_being_used = True

        db.session.add(ubr_info_2)
        db.session.commit()

    set_default_group(user_info)
