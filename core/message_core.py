# -*- coding: utf-8 -*-
import copy

from configs.config import MSG_TYPE_SYS, MSG_TYPE_TXT, db, CONTENT_TYPE_SYS, CONTENT_TYPE_TXT
from models.android_db_models import AMessage, AMember, AContact
from models.chatroom_member_models import BotChatroomR, ChatroomInfo, ChatroomStatistic, MemberInfo, MemberStatistic, \
    ChatroomActive, MemberAtMember, MemberInviteMember, MemberOverview
from models.message_ext_models import MessageAnalysis
from utils.u_time import get_today_0
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
            # 收到的群消息没有 ':\n', "语言聊天已结束" 等
            real_talker = talker
        else:
            content_part = content.split(u':')
            real_talker = content_part[0]
    else:
        if content.find(u':\n') == -1:
            # Mark: 收到的群消息没有 ':\n'，需要查错
            logger.info(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(
                msg_ext.msg_id) + u" type: " + unicode(msg_type))
            raise ValueError(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(
                msg_ext.msg_id) + u" type: " + unicode(msg_type))
        content_part = content.split(u':\n')
        real_talker = content_part[0]
        real_content = content_part[1]

    msg_ext.real_talker = real_talker
    msg_ext.real_content = unicode_to_str(real_content)

    return msg_ext


def count_msg_by_ids(start_id, end_id):
    print 'start', start_id, 'end', end_id
    try:
        msg_list = db.session.query(MessageAnalysis).filter(MessageAnalysis.msg_id >= start_id,
                                                            MessageAnalysis.msg_id <= end_id).all()
        for msg in msg_list:
            count_msg(msg)
    except Exception:
        db.session.rollback()
        logger.exception("Exception")
    finally:
        # logger.info('count_msg db.session.close()')
        db.session.close()


def count_msg(msg):
    today = get_today_0()

    if msg.is_to_friend:
        pass
    else:
        content = str_to_unicode(msg.content)
        chatroomname = msg.talker
        username = msg.real_talker
        # is_send = msg.is_send
        msg_type = msg.type

        # TODO: 在内存中，用全局标识控制更新
        bot_chatroom_r = db.session.query(BotChatroomR).filter(BotChatroomR.chatroomname == chatroomname,
                                                               BotChatroomR.username == msg.username,
                                                               BotChatroomR.is_on == 1).first()
        if bot_chatroom_r:
            chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroomname == chatroomname).first()

            chatroom_id = chatroom.chatroom_id

            # calc chatroom statics
            logger.info('calc chatroom statistics')
            chatroom_statistic = ChatroomStatistic.fetch_chatroom_statistics(chatroom_id = chatroom_id,
                                                                             time_to_day = today)
            logger.info('| speak_count')
            if msg_type != CONTENT_TYPE_SYS:
                chatroom_statistic.speak_count += 1
                chatroom.total_speak_count += 1
                member = fetch_member_by_username(chatroomname, username)
                if not member:
                    logger.error(u"find no member, chatroomname: %s, username: %s." % (chatroomname, username))
                    return
                talker_id = member.member_id

                # calc member statics
                logger.info('calc member   statistics')
                member_statistic = MemberStatistic.fetch_member_statistics(member_id = talker_id,
                                                                           time_to_day = today,
                                                                           chatroom_id = chatroom_id)
                logger.info('| speak_count')
                member_statistic.speak_count += 1
                member.speak_count += 1

                chatroom_active = ChatroomActive(member_id = member.member_id, chatroom_id = chatroom.chatroom_id,
                                                 time_to_day = today, create_time = msg.create_time)
                db.session.merge(chatroom_active)

                if msg_type == CONTENT_TYPE_TXT:
                    if content.find(u'@') != -1:
                        logger.info('| be_at_count')
                        at_count = extract_msg_be_at(msg, chatroom)
                        if msg.is_at:
                            chatroom_statistic.at_count += at_count
                            chatroom.total_at_count += at_count

            db.session.commit()

            if msg_type == CONTENT_TYPE_SYS:
                # 被邀请入群
                # Content="frank5433"邀请你和"秦思语-Doodod、磊"加入了群聊
                # "Sw-fQ"邀请你加入了群聊，群聊参与人还有：qiezi、Hugh、蒋郁、123
                if content.find(u'邀请你') != -1:
                    logger.info(u'invite_bot')
                    invite_bot(msg, chatroom)
                # 其他人入群：邀请、扫码
                # "斗西"邀请"陈若曦"加入了群聊
                # " BILL"通过扫描"谢工@GitChat&图灵工作用"分享的二维码加入群聊
                # "風中落葉🍂"邀请"大冬天的、追忆那年的似水年华、往事随风去、搁浅、陈梁～HILTI"加入了群聊
                elif content.find(u'加入了群聊') != -1 or content.find(u'加入群聊') != -1:
                    logger.info(u'invite_other')
                    invite_other(msg, chatroom)

            db.session.commit()

            # content_type = CONTENT_TYPE_UNKNOWN
            # if msg_type == CONTENT_TYPE_TXT:
            #     content_type = CONTENT_TYPE_TXT
            # elif msg_type == CONTENT_TYPE_PIC:
            #     content_type = CONTENT_TYPE_PIC
            # elif msg_type == CONTENT_TYPE_MP3:
            #     content_type = CONTENT_TYPE_MP3
            # elif msg_type == CONTENT_TYPE_MP4:
            #     content_type = CONTENT_TYPE_MP4
            # elif msg_type == CONTENT_TYPE_GIF:
            #     content_type = CONTENT_TYPE_GIF
            # elif msg_type == CONTENT_TYPE_VIDEO:
            #     content_type = CONTENT_TYPE_VIDEO
            # elif msg_type == CONTENT_TYPE_SHARE:
            #     content_type = CONTENT_TYPE_SHARE
            # elif msg_type == CONTENT_TYPE_NAME_CARD:
            #     content_type = CONTENT_TYPE_NAME_CARD
            # elif msg_type == CONTENT_TYPE_SYS:
            #     content_type = CONTENT_TYPE_SYS
            #     # 红包
            #     if content == u'收到红包，请在手机上查看':
            #         logger.info(u'收到红包')
            #         content_type = CONTENT_TYPE_RED
            #     # 被邀请入群
            #     # Content="frank5433"邀请你和"秦思语-Doodod、磊"加入了群聊
            #     # "Sw-fQ"邀请你加入了群聊，群聊参与人还有：qiezi、Hugh、蒋郁、123
            #     elif content.find(u'邀请你') != -1:
            #         logger.info(u'invite_bot')
            #         MessageAnalysis.invite_bot(msg, chatroom)
            #
            #     # 其他人入群：邀请、扫码
            #     # "斗西"邀请"陈若曦"加入了群聊
            #     # " BILL"通过扫描"谢工@GitChat&图灵工作用"分享的二维码加入群聊
            #     # "風中落葉🍂"邀请"大冬天的、追忆那年的似水年华、往事随风去、搁浅、陈梁～HILTI"加入了群聊
            #     elif content.find(u'加入了群聊') != -1 or content.find(u'加入群聊') != -1:
            #         logger.info(u'invite_other')
            #         MessageAnalysis.invite_other(msg, chatroom)
            #
            #     # 修改群名
            #     # "阿紫"修改群名为“测试群”
            #     elif content.find(u'修改群名为') != -1:
            #         logger.info(u'修改群名')
            #         chatroom_nick_name = content.split(u'修改群名为')[1][1:-1]
            #         logger.info(u'chatroom_nick_name: ' + chatroom_nick_name)
            #         chatroom.nick_name = chatroom_nick_name
            #     # 移除群聊
            #     elif content.find(u'移除群聊') != -1:
            #         pass
            #     else:
            #         logger.info('UNKOWN SYS INFO: ')
            #         logger.info(content)
            #     db.session.commit()
            #
            # # calc content_type
            # logger.info('calc chatroom content type')
            # logger.info('calc member   content type')
            # chatroom_content_type = ChatroomContentType.get_chatroom_content_type(chatroom_id = chatroom_id,
            #                                                                       content_type = content_type)
            #
            # chatroom_content_type.incre()
            # if content_type is not CONTENT_TYPE_SYS and content_type is not CONTENT_TYPE_RED:
            #     member = db.session.query(Member).filter(Member.member_name == username).first()
            #     talker_id = member.id
            #     member_content_type = MemberContentType.get_member_content_type(member_id = talker_id,
            #                                                                     content_type = content_type)
            #     member_content_type.incre()
            #     if content_type is CONTENT_TYPE_SHARE:
            #         pass
            #
            # db.session.commit()


def extract_msg_be_at(msg, chatroom):
    at_count = 0
    content = str_to_unicode(msg.real_content)
    content_tmp = copy.deepcopy(content)
    today = get_today_0()
    member = db.session.query(MemberInfo).filter(MemberInfo.username == msg.real_talker).first()
    if not member:
        logger.error(u"找不到 member: " + str_to_unicode(msg.real_talker))
        return

    print u''
    chatroom_id = chatroom.chatroom_id
    if content_tmp.find(u'@') != -1:
        msg.is_at = True
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
                    msg.is_at = False
                    break
                if name_be_at.find(u'\u2005') != -1:
                    name_be_at = name_be_at.replace(u'\u2005', u' ')
                    print name_be_at.__repr__()
                logger.debug(u'nick_name_be_at: ' + name_be_at)
                member_be_at = fetch_member_by_nickname(chatroomname = chatroom.chatroomname,
                                                        nickname = name_be_at)
                # 匹配到 member
                if member_be_at:
                    msg.is_at = True
                    offset += end_index
                    logger.info(u'member_be_at ' + str(member_be_at.member_id))
                    member_be_at.be_at_count += 1
                    member_be_at_id = member_be_at.member_id
                    msg.member_id_be_at = member_be_at_id
                    msg.name_be_at = name_be_at
                    member_statics_be_at = MemberStatistic.fetch_member_statistics(member_id = member_be_at_id,
                                                                                   time_to_day = today,
                                                                                   chatroom_id = chatroom_id)
                    member_statics_be_at.be_at_count += 1
                    mam = MemberAtMember(from_member_id = member.member_id, from_username = member.username,
                                         to_member_id = member_be_at_id, to_username = member_be_at.username,
                                         create_time = msg.create_time)
                    db.session.merge(mam)
                    db.session.commit()

                    at_count += 1
                    break
                else:
                    # logger.info(u'not find ' + name_be_at)
                    # 没有匹配到 member
                    # if not checked_flag:
                    #     # check
                    #     checked_flag = True
                    #     # check
                    #     MessageAnalysis.check_chatroom(chatroom)
                    #     end_index = 0
                    # else:
                    logger.info(u'really not find ' + name_be_at)
            content_index = offset
    return at_count


def invite_bot(msg, chatroom):
    content = str_to_unicode(msg.real_content)
    content_tmp = copy.deepcopy(content)
    print u''
    invitor_nick_name = content_tmp.split(u'邀请')[0][1:-1]
    logger.debug(u'invitor_nick_name: ' + invitor_nick_name)

    invited_nick_name_list = list()
    if content_tmp.find(u'邀请你和') != -1:
        start_index = content_tmp.find(u'邀请你和')
        end_index = content_tmp.rfind(u'"加入')
        invited_nick_names = content_tmp[start_index + 5:end_index]
        invited_nick_name_list = invited_nick_names.split(u'、')

    invitor = fetch_member_by_nickname(chatroomname = chatroom.chatroomname,
                                       nickname = invitor_nick_name)
    if invitor:
        # filter_list_wechat = Wechat.get_filter_list()
        # filter_list_wechat.append(Wechat.nick_name == invitor.nick_name)
        # filter_list_wechat.append(Wechat.sex == invitor.sex)
        # filter_list_wechat.append(Wechat.city == invitor.city)
        # filter_list_wechat.append(Wechat.province == invitor.province)
        # invitor_wechat = db.session.query(Wechat).filter(*filter_list_wechat).first()
        # if invitor_wechat:
        #     logger.info('invitor_wechat: ' + str(invitor_wechat.id))
        #     observer = Observer(wechat_id = invitor_wechat.id, chatroom_id = chatroom_id,
        #                         is_on = True).generate_create_time()
        #     db.session.merge(observer)
        for invited_nick_name in invited_nick_name_list:
            logger.debug(u'invited_nick_name: ' + invited_nick_name)
            invited = fetch_member_by_nickname(chatroomname = chatroom.chatroomname,
                                               nickname = invited_nick_name)
            if invited:
                m_i_m = MemberInviteMember(invitor_id = invitor.member_id, invited_id = invited.member_id,
                                           create_time = msg.create_time, invited_username = invited.username,
                                           invitor_username = invitor.username)
                db.session.merge(m_i_m)
    db.session.commit()


def invite_other(msg, chatroom):
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

    invitor = fetch_member_by_nickname(chatroomname = chatroom.chatroomname,
                                       nickname = invitor_nick_name)
    if invitor:
        for invited_nick_name in invited_nick_name_list:
            logger.debug(u'invited_nick_name: ' + invited_nick_name)
            invited = fetch_member_by_nickname(chatroomname = chatroom.chatroomname,
                                               nickname = invited_nick_name)
            if invited:
                m_i_m = MemberInviteMember(invitor_id = invitor.member_id, invited_id = invited.member_id,
                                           create_time = msg.create_time, invited_username = invited.username,
                                           invitor_username = invitor.username)
                db.session.merge(m_i_m)
    db.session.commit()


def fetch_member_by_nickname(chatroomname, nickname):
    member = None
    if nickname:
        # 匹配 AMember
        a_member = db.session.query(AMember).filter(AMember.displayname == nickname,
                                                    AMember.chatroomname == chatroomname).first()
        if not a_member:
            # 匹配 AContact
            a_contact = db.session.query(AContact).outerjoin(AMember, AMember.username == AContact.username)\
                .filter(AContact.nickname == unicode_to_str(nickname), AMember.chatroomname == chatroomname).first()
            if a_contact:
                member = fetch_member_by_username(chatroomname, a_contact.username)
            else:
                logger.error(u"未匹配到 member, nickname: %s, chatroom: %s" % (nickname, chatroomname))
        else:
            member = fetch_member_by_username(chatroomname, a_member.username)

    return member


def fetch_member_by_username(chatroomname, username):
    member = db.session.query(MemberInfo).filter(MemberInfo.chatroomname == chatroomname,
                                                 MemberInfo.username == username).first()
    if not member:
        MemberInfo.update_members(chatroomname, save_flag = True)
        # 更新信息之后再查不到就不管了
        member = db.session.query(MemberInfo).filter(MemberInfo.chatroomname == chatroomname,
                                                     MemberInfo.username == username).first()

    return member


def update_members(chatroomname, create_time = None, save_flag = False):
    a_contact_chatroom = db.session.query(AContact).filter(AContact.username == chatroomname).first()
    if not a_contact_chatroom:
        logger.error(u'Not found chatroomname in AContact: %s.' % chatroomname)
        return
    old_members = db.session.query(MemberInfo.username).filter(MemberInfo.chatroomname == chatroomname).all()
    # old_member_dict = {old_member.username: old_member for old_member in old_members}
    old_member_username_set = {old_member.username for old_member in old_members}
    a_member_list = db.session.query(AMember).filter(AMember.chatroomname == chatroomname).all()
    for a_member in a_member_list:
        if a_member.username in old_member_username_set:
            pass
        else:
            new_member_info = MemberInfo(member_id = a_member.id, chatroomname = chatroomname,
                                         username = a_member.username, chatroom_id = a_contact_chatroom.id) \
                .generate_create_time(create_time)

            MemberOverview.init_all_scope(member_id = a_member.id, chatroom_id = a_contact_chatroom.id,
                                          chatroomname = chatroomname, username = a_member.username)
            db.session.merge(new_member_info)

    if save_flag:
        db.session.commit()
