# -*- coding: utf-8 -*-
__author__ = "quentin"

from models_v2.base_model import BaseModel
from core_v2.send_msg import send_ws_to_android
from configs.config import SUCCESS, UserBotR

import logging
import time

logger = logging.getLogger('main')


def check_is_at_bot(a_message):
    # Check if @ bot and content is right.
    logger.info('[check is at bot]')
    real_talker = a_message.real_talker
    message_list = a_message.content.split()
    chatroomname = a_message.talker

    if len(message_list) != 3:
        return

    if message_list[0][:-1] == real_talker and message_list[1].startswith(u'@') and message_list[2] == u'激活小助手':
        client = BaseModel.fetch_one("client_qun_r", "*",
                                     where_clause=BaseModel.and_(
                                         ["=", "chatroomname", chatroomname]
                                     ))
        client.is_paid = 1
        client.save()

        time.sleep(5)
        # 通知付费成功信息
        ubr = BaseModel.fetch_one(UserBotR, '*',
                                  where_clause=BaseModel.where_dict({"client_id": client.client_id}))
        try:
            chatroomname = BaseModel.fetch_one("a_chatroom", "*",
                                               where_clause=BaseModel.and_(
                                                   ["=", "chatroomname", chatroomname]
                                               )).nickname_real
            if not chatroomname:
                chatroomname = u"您的群聊"
        except Exception:
            chatroomname = u"您的群聊"

        chatroomname = chatroomname if chatroomname == u"您的群聊" else u'<' + chatroomname + u'>'
        info_data = {
            "task": "send_message",
            "to": a_message.real_talker,
            "type": 1,
            "content": u"谢谢您付费，小助手已经在为您的%s群提供服务啦！" % chatroomname
        }

        try:
            status = send_ws_to_android(ubr.bot_username, info_data)
            if status == SUCCESS:
                logger.info(u"激活群通知任务发送成功, client_id: %s." % client.client_id)
            else:
                logger.info(u"激活群通知任务发送失败, client_id: %s." % client.client_id)
        except Exception:
            pass

        print "########################################################3"
