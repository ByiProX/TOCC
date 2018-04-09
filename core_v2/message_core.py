# -*- coding: utf-8 -*-
import copy
import json

from configs.config import MSG_TYPE_SYS, MSG_TYPE_TXT, db, CONTENT_TYPE_SYS, CONTENT_TYPE_TXT, CHAT_LOGS_TYPE_2, \
    CHAT_LOGS_TYPE_1, CHAT_LOGS_TYPE_3, rds, Member, Contact, CHAT_LOGS_ERR_TYPE_0
from core.redis_core import rds_lpush
from core.send_task_and_ws_setting_core import update_chatroom_members_info
from models_v2.base_model import BaseModel
from utils.u_time import get_today_0
from utils.u_transformat import str_to_unicode, unicode_to_str

import logging

logger = logging.getLogger('main')


def count_msg(msg):
    if msg.is_to_friend:
        pass
    else:
        content = str_to_unicode(msg.content)
        chatroomname = msg.talker
        username = msg.real_talker
        msg_type = msg.type

        if msg_type == CONTENT_TYPE_TXT and content.find(u'@') != -1:
                logger.info(u'| be_at_count')
                is_at, at_count = extract_msg_be_at(msg, chatroomname)

        if msg_type == CONTENT_TYPE_SYS:
            # 被邀请入群
            # Content="frank5433"邀请你和"秦思语-Doodod、磊"加入了群聊
            # "Sw-fQ"邀请你加入了群聊，群聊参与人还有：qiezi、Hugh、蒋郁、123
            if content.find(u'邀请你') != -1:
                logger.info(u'invite_bot')
                invite_bot(msg, chatroomname)
            # 其他人入群：邀请、扫码
            # "斗西"邀请"陈若曦"加入了群聊
            # " BILL"通过扫描"谢工@GitChat&图灵工作用"分享的二维码加入群聊
            # "風中落葉🍂"邀请"大冬天的、追忆那年的似水年华、往事随风去、搁浅、陈梁～HILTI"加入了群聊
            elif content.find(u'加入了群聊') != -1 or content.find(u'加入群聊') != -1:
                logger.info(u'invite_other')
                invite_other(msg, chatroomname)


def extract_msg_be_at(msg, chatroomname):
    at_count = 0
    is_at = False
    member_be_at_list = list()
    content = str_to_unicode(msg.real_content)
    content_tmp = copy.deepcopy(content)

    if content_tmp.find(u'@') != -1:
        is_at = True
        content_index = 0
        while content_tmp[content_index:].find(u'@') != -1:
            offset = content_index + content_tmp[content_index:].find(u'@') + 1
            end_index = 0
            if content_tmp[content_index:].find(u'\u2005') == -1:
                content_tmp = content_tmp.replace(u' ', u'\u2005')
                # print content_tmp.__repr__()
            while content_tmp[offset + end_index:].find(u'\u2005') != -1:
                end_index += content_tmp[offset + end_index:].find(u'\u2005') + 1
                name_be_at = content_tmp[offset:offset + end_index - 1]
                if name_be_at == u'':
                    is_at = False
                    break
                if name_be_at.find(u'\u2005') != -1:
                    name_be_at = name_be_at.replace(u'\u2005', u' ')
                logger.debug(u'nick_name_be_at: ' + name_be_at)
                member_be_at = fetch_member_by_nickname(chatroomname = chatroomname,
                                                        nickname = name_be_at)
                # 匹配到 member
                if member_be_at:
                    logger.info(u'member_be_at ' + unicode(member_be_at))
                    is_at = True
                    offset += end_index
                    member_be_at_list.append(member_be_at)
                    at_count += 1
                    break
                else:
                    logger.info(u'really not find ' + name_be_at)
                    rds_lpush(chat_logs_type = CHAT_LOGS_ERR_TYPE_0, msg_id = msg.get_id(), err = True)
                    # Mark 一个异常，全部异常
                    return
            content_index = offset

    if is_at and member_be_at_list:
        chat_logs_type = CHAT_LOGS_TYPE_3
        content = json.dumps(member_be_at_list)
    else:
        chat_logs_type = CHAT_LOGS_TYPE_2
        content = ""
    rds_lpush(chat_logs_type, msg.get_id(), msg.talker, msg.real_talker, msg.create_time, content)
    return is_at, at_count


def invite_bot(msg, chatroomname):
    content = str_to_unicode(msg.real_content)
    content_tmp = copy.deepcopy(content)
    invitor_nick_name = content_tmp.split(u'邀请')[0][1:-1]
    logger.debug(u'invitor_nick_name: ' + invitor_nick_name)

    invited_username_list = list()
    invited_username_list.append(msg.bot_username)

    invited_nick_name_list = list()
    if content_tmp.find(u'邀请你和') != -1:
        start_index = content_tmp.find(u'邀请你和')
        end_index = content_tmp.rfind(u'"加入')
        invited_nick_names = content_tmp[start_index + 5:end_index]
        invited_nick_name_list = invited_nick_names.split(u'、')

    invitor = fetch_member_by_nickname(chatroomname = chatroomname,
                                       nickname = invitor_nick_name)
    if invitor:
        for invited_nick_name in invited_nick_name_list:
            logger.debug(u'invited_nick_name: ' + invited_nick_name)
            invited = fetch_member_by_nickname(chatroomname = chatroomname,
                                               nickname = invited_nick_name)
            if invited:
                logger.info(u'invited ' + unicode(invited))
                invited_username_list.append(invited)
            else:
                logger.info(u'really not find ' + invited_nick_name)
                rds_lpush(chat_logs_type = CHAT_LOGS_ERR_TYPE_0, msg_id = msg.get_id(), err = True)
                # Mark 一个异常，全部异常
                return

        chat_logs_type = CHAT_LOGS_TYPE_1
        content = json.dumps(invited_username_list)
        rds_lpush(chat_logs_type, msg.get_id(), msg.talker, invitor, msg.create_time, content)


def invite_other(msg, chatroomname):
    content = str_to_unicode(msg.real_content)
    content_tmp = copy.deepcopy(content)
    print u''
    if content_tmp.find(u'邀请') != -1:
        invitor_nick_name = content_tmp.split(u'邀请')[0][1:-1]
        logger.debug(u'invitor_nick_name: ' + invitor_nick_name)
        # "斗西"邀请"陈若曦"加入了群聊
        # "風中落葉🍂"邀请"大冬天的、追忆那年的似水年华、往事随风去、搁浅、陈梁～HILTI"加入了群聊
        start_index = content_tmp.find(u'邀请')
        end_index = content_tmp.rfind(u'"加入')
        invited_nick_names = content_tmp[start_index + 3:end_index]
        invited_nick_name_list = invited_nick_names.split(u'、')

    # " BILL"通过扫描"谢工@GitChat&图灵工作用"分享的二维码加入群聊
    elif content_tmp.find(u'通过扫描') != -1:
        nick_names = content_tmp.split(u'通过扫描')
        invited_nick_name = nick_names[0][2:-1]
        end_index = nick_names[1].rfind(u'"分享')
        invitor_nick_name = nick_names[1][1:end_index]
        logger.debug(u'invitor_nick_name: ' + invitor_nick_name)
        invited_nick_name_list = [invited_nick_name]
    else:
        logger.info(u'unknown invite type: ')
        logger.info(msg.content)
        return

    invited_username_list = list()
    invitor = fetch_member_by_nickname(chatroomname = chatroomname,
                                       nickname = invitor_nick_name)
    if invitor:
        for invited_nick_name in invited_nick_name_list:
            logger.debug(u'invited_nick_name: ' + invited_nick_name)
            invited = fetch_member_by_nickname(chatroomname = chatroomname,
                                               nickname = invited_nick_name)
            if invited:
                logger.info(u'invited ' + unicode(invited))
                invited_username_list.append(invited)
            else:
                logger.info(u'really not find ' + invited_nick_name)
                rds_lpush(chat_logs_type = CHAT_LOGS_ERR_TYPE_0, msg_id = msg.get_id(), err = True)
                # Mark 一个异常，全部异常
                return

        if invited_username_list:
            chat_logs_type = CHAT_LOGS_TYPE_1
            content = json.dumps(invited_username_list)
            rds_lpush(chat_logs_type, msg.get_id(), msg.talker, invitor, msg.create_time, content)


def fetch_member_by_nickname(chatroomname, nickname, update_flag = True):
    member = None
    if nickname:
        # 匹配 AMember
        a_member = BaseModel.fetch_one(Member, "*", where_clause = BaseModel.where_dict({"chatroomname": chatroomname}))
        members = a_member.members
        for member in members:
            # Mark 不处理匹配到多个的情况
            if member.displayname == nickname:
                return member.username
        member_usernames = [member.username for member in members]
        a_contact_list = BaseModel.fetch_all(Contact, ["username", "nickname"], where_clause = BaseModel.where("in", "username", member_usernames))
        for a_contact in a_contact_list:
            # Mark 不处理匹配到多个的情况
            if a_contact.nickname == nickname:
                return a_contact.username

    if update_flag:
        update_members(chatroomname)
        return fetch_member_by_nickname(chatroomname, nickname, update_flag = False)
    return member


def update_members(chatroomname, create_time = None, save_flag = False):
    # a_contact_chatroom = db.session.query(AContact).filter(AContact.username == chatroomname).first()
    # if not a_contact_chatroom:
    #     logger.error(u'Not found chatroomname in AContact: %s.' % chatroomname)
    #     return
    # old_members = db.session.query(MemberInfo.username).filter(MemberInfo.chatroomname == chatroomname).all()
    # # old_member_dict = {old_member.username: old_member for old_member in old_members}
    # old_member_username_set = {old_member.username for old_member in old_members}
    # a_member_list = db.session.query(AMember).filter(AMember.chatroomname == chatroomname).all()
    # for a_member in a_member_list:
    #     if a_member.username in old_member_username_set:
    #         pass
    #     else:
    #         old_member_username_set.add(a_member.username)
    #         new_member_info = MemberInfo(member_id = a_member.id, chatroomname = chatroomname,
    #                                      username = a_member.username, chatroom_id = a_contact_chatroom.id) \
    #             .generate_create_time(create_time)
    #
    #         MemberOverview.init_all_scope(member_id = a_member.id, chatroom_id = a_contact_chatroom.id,
    #                                       chatroomname = chatroomname, username = a_member.username)
    #         db.session.merge(new_member_info)
    #
    # update_chatroom_members_info(chatroomname)
    # if save_flag:
    #     db.session.commit()
    pass
