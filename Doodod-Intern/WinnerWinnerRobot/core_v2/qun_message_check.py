# -*- coding: utf-8 -*-
__author__ = "quentin"

from models_v2.base_model import BaseModel
import logging

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
        print "########################################################3"
