# -*- coding: utf-8 -*-
from configs.config import MSG_TYPE_SYS, MSG_TYPE_TXT
from models.android_db_models import AMessage
from models.message_ext_models import MessageAnalysis
from utils.u_transformat import str_to_unicode, unicode_to_str

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
    msg_type = msg_ext.type

    # is_to_friend
    if msg_ext.talker.find(u'@chatroom') != -1:
        is_to_friend = False
    else:
        is_to_friend = True
    msg_ext.is_to_friend = is_to_friend

    # real_talker & real_content
    if is_to_friend or is_send or msg_type == MSG_TYPE_SYS:
        real_talker = talker
        real_content = content
    elif msg_type != MSG_TYPE_TXT:
        # 除了 TXT 和 SYS 的处理
        real_content = content
        if content.find(u':') == -1:
            # Mark: 收到的群消息没有 ':\n'，需要查错
            logger.info(u"ERR: chatroom msg received doesn't have ':', msg_id: " + unicode(msg_ext.msg_id) + u" type: " + unicode(msg_type))
            raise ValueError(u"ERR: chatroom msg received doesn't have ':', msg_id: " + unicode(msg_ext.msg_id) + u" type: " + unicode(msg_type))
        content_part = content.split(u':')
        real_talker = content_part[0]
    else:
        if content.find(u':\n') == -1:
            # Mark: 收到的群消息没有 ':\n'，需要查错
            logger.info(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(msg_ext.msg_id) + u" type: " + unicode(msg_type))
            raise ValueError(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(msg_ext.msg_id) + u" type: " + unicode(msg_type))
        content_part = content.split(u':\n')
        real_talker = content_part[0]
        real_content = content_part[1]

    msg_ext.real_talker = real_talker
    msg_ext.real_content = unicode_to_str(real_content)

    return msg_ext
