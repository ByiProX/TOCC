# -*- coding: utf-8 -*-
from models.android_db import AMessage
from models.message_ext import MessageAnalysis
from utils.u_str_unicode import str_to_unicode, unicode_to_str

import logging

logger = logging.getLogger('main')


def analysis_and_save_a_message(a_message):
    """
    用于将a_message信息放入库中，并返回库中的结构模样
    :param a_message:
    :return:
    """
    if not isinstance(a_message, AMessage):
        # Mark
        # 几乎不报错，报错需要查错
        raise TypeError(u'AMessage Type Err')
    msg_ext = MessageAnalysis(a_message)
    content = str_to_unicode(msg_ext.content)
    is_send = msg_ext.is_send
    talker = msg_ext.talker

    # is_to_friend
    if msg_ext.username.find(u'@chatroom') != -1:
        is_to_friend = False
    else:
        is_to_friend = True
    msg_ext.is_to_friend = is_to_friend

    # real_talker & real_content
    if is_to_friend or is_send:
        real_talker = talker
        real_content = content
    else:
        if content.find(u':\n') != -1:
            # Mark: 收到的群消息没有 ':\n'，需要查错
            logger.info(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(msg_ext.msg_id))
            raise ValueError(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(msg_ext.msg_id))
        content_part = content.split(u':\n')
        real_talker = content_part[0]
        real_content = content_part[1]

    msg_ext.real_talker = real_talker
    msg_ext.real_content = unicode_to_str(real_content)

    return msg_ext
