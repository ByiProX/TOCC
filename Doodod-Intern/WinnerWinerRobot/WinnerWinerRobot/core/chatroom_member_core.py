# -*- coding: utf-8 -*-

import logging
from datetime import timedelta, datetime

from decimal import Decimal
from sqlalchemy import func, distinct

from configs.config import db, SCOPE_24_HOUR, MSG_TYPE_TXT, MSG_TYPE_SYS
from models.android_db_models import AMember, AContact
from models.chatroom_member_models import ChatroomInfo, ChatroomStatistic, ChatroomOverview, ChatroomActive, \
    MemberStatistic, MemberOverview, MemberInviteMember
from models.message_ext_models import MessageAnalysis
from utils.u_time import get_today_0, get_time_window_by_scope

logger = logging.getLogger('main')


def update_all_member_count(chatroom_statistics):
    if not isinstance(chatroom_statistics, ChatroomStatistic):
        logger.error(u'update_all_member_count: not a entity of ChatroomStatistic')
        logger.error(u'type: ', type(chatroom_statistics))
        return chatroom_statistics
    start_time = chatroom_statistics.time_to_day
    end_time = start_time + timedelta(days = 1)
    chatroom = db.session.query(ChatroomInfo)\
        .filter(ChatroomInfo.chatroom_id == chatroom_statistics.chatroom_id).first()
    filter_list_total = AMember.get_filter_list(chatroomname = chatroom.chatroomname, is_deleted = False,
                                                end_time = end_time)
    filter_list_total.append(AContact.id > 0)
    filter_list_in = AMember.get_filter_list(chatroomname = chatroom.chatroomname, is_deleted = False,
                                             start_time = start_time, end_time = end_time)
    filter_list_in.append(AMember.create_time > chatroom.create_time)
    filter_list_in.append(AContact.id > 0)
    filter_list_out = AMember.get_filter_list(chatroomname = chatroom.chatroomname, is_deleted = True)
    filter_list_out.append(AMember.update_time >= start_time)
    filter_list_out.append(AMember.update_time < end_time)
    members_in = db.session.query(func.count(AMember.id)) \
        .outerjoin(AContact, AMember.username == AContact.username) \
        .filter(*filter_list_in).first()[0] or 0
    members_out = db.session.query(func.count(AMember.id)) \
        .outerjoin(AContact, AMember.username == AContact.username) \
        .filter(*filter_list_out).first()[0] or 0
    member_count = db.session.query(func.count(AMember.id)) \
        .outerjoin(AContact, AMember.username == AContact.username) \
        .filter(*filter_list_total).first()[0] or 0
    chatroom_statistics.in_count = members_in
    chatroom_statistics.out_count = members_out
    chatroom_statistics.member_count = member_count
    chatroom_statistics.generate_update_time()
    return chatroom_statistics


def batch_update_chatroom_overview(chatroom_overview, chatroom_create_time, save_flag = False):
    if not isinstance(chatroom_overview, ChatroomOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(chatroom_overview))
        return chatroom_overview
    today = get_today_0()
    chatroom_statistic = ChatroomStatistic.fetch_chatroom_statistics(chatroom_id = chatroom_overview.chatroom_id,
                                                                     time_to_day = today)

    update_all_member_count(chatroom_statistic)
    update_speak_count(chatroom_overview, chatroom_create_time)
    update_incre_count(chatroom_overview, chatroom_create_time)
    update_active_count(chatroom_overview, chatroom_create_time)
    update_active_rate(chatroom_overview, chatroom_statistic.member_count)
    update_active_class(chatroom_overview)
    update_member_change(chatroom_overview, chatroom_create_time)
    if save_flag:
        db.session.commit()
    chatroom_overview.generate_update_time()
    return chatroom_overview


def update_speak_count(chatroom_overview, chatroom_create_time, save_flag = False):
    if not isinstance(chatroom_overview, ChatroomOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(chatroom_overview))
        return chatroom_overview
    if chatroom_overview.scope == SCOPE_24_HOUR:
        end_time = datetime.now()
        start_time = end_time - timedelta(days = 1)
        # MessageAnalysis
        filter_list_ma = MessageAnalysis.get_filter_list(start_time = start_time, end_time = end_time)
        filter_list_ma.append(MessageAnalysis.type < MSG_TYPE_SYS)
        filter_list_ma.append(MessageAnalysis.talker == chatroom_overview.chatroomname)
        filter_list_ma.append(MessageAnalysis.create_time >= chatroom_create_time)
        speak_count = db.session.query(func.count(MessageAnalysis.msg_id))\
            .filter(*filter_list_ma).first()[0] or 0
    else:
        start_time, end_time = get_time_window_by_scope(scope = chatroom_overview.scope)
        # ChatroomStatistics
        filter_list_cs = ChatroomStatistic.get_filter_list(chatroom_id = chatroom_overview.chatroom_id,
                                                           start_time = start_time, end_time = end_time)
        speak_count = 0
        cs_list = db.session.query(ChatroomStatistic).filter(*filter_list_cs).all()
        for cs in cs_list:
            speak_count += cs.speak_count

    chatroom_overview.speak_count = speak_count
    if save_flag:
        db.session.commit()
    chatroom_overview.generate_update_time()
    return chatroom_overview


def update_incre_count(chatroom_overview, chatroom_create_time, save_flag = False):
    if not isinstance(chatroom_overview, ChatroomOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(chatroom_overview))
        return chatroom_overview
    if chatroom_overview.scope == SCOPE_24_HOUR:
        end_time = datetime.now()
        start_time = end_time - timedelta(days = 1)
    else:
        start_time, end_time = get_time_window_by_scope(scope = chatroom_overview.scope)
    # both from AMember
    filter_list_am = AMember.get_filter_list(chatroomname = chatroom_overview.chatroomname, start_time = start_time,
                                             end_time = end_time, is_deleted = False)
    filter_list_am.append(AMember.create_time > chatroom_create_time)
    incre_count = db.session.query(func.count(AMember.id)).filter(*filter_list_am).first()[0] or 0

    chatroom_overview.incre_count = incre_count
    if save_flag:
        db.session.commit()
    chatroom_overview.generate_update_time()
    return chatroom_overview


def update_active_count(chatroom_overview, chatroom_create_time, save_flag = False):
    if not isinstance(chatroom_overview, ChatroomOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(chatroom_overview))
        return chatroom_overview
    if chatroom_overview.scope == SCOPE_24_HOUR:
        end_time = datetime.now()
        start_time = end_time - timedelta(days = 1)
    else:
        start_time, end_time = get_time_window_by_scope(scope = chatroom_overview.scope)
    # both from ChatroomActive
    filter_list_ca = ChatroomActive.get_filter_list(chatroom_id = chatroom_overview.chatroom_id,
                                                    start_time = start_time,
                                                    end_time = end_time)
    filter_list_ca.append(ChatroomActive.create_time >= chatroom_create_time)
    active_count = db.session.query(func.count(distinct(ChatroomActive.member_id)))\
        .filter(*filter_list_ca).first()[0] or 0

    chatroom_overview.active_count = active_count
    if save_flag:
        db.session.commit()
    chatroom_overview.generate_update_time()
    return chatroom_overview


def update_active_rate(chatroom_overview, member_count = None, save_flag = False):
    if not isinstance(chatroom_overview, ChatroomOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(chatroom_overview))
        return chatroom_overview
    if not member_count:
        a_contact_chatroom = db.session.query(AContact).filter(AContact.id == chatroom_overview.chatroom_id).first()
        if a_contact_chatroom:
            member_count = a_contact_chatroom.member_count
        else:
            # Mark
            # AContact 里面没有找到该 Chatroom, do nothing just return
            # member_count = MAX_MEMBER_COUNT_DECIMAL
            logger.error(u'no such chatroom_id in AContact: %s.' % str(chatroom_overview.chatroom_id))
            return chatroom_overview
    chatroom_overview.active_rate = Decimal(chatroom_overview.active_count) / Decimal(member_count)
    if save_flag:
        db.session.commit()
    chatroom_overview.generate_update_time()
    return chatroom_overview


def update_member_change(chatroom_overview, chatroom_create_time, save_flag = False):
    if chatroom_overview.scope == 24:
        end_time = datetime.now()
        start_time = end_time - timedelta(days = 1)
    else:
        start_time, end_time = get_time_window_by_scope(chatroom_overview.scope)
    chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroom_id == chatroom_overview.chatroom_id).first()
    filter_list_in = AMember.get_filter_list(chatroomname = chatroom.chatroomname, is_deleted = False,
                                             start_time = start_time, end_time = end_time)
    filter_list_in.append(AMember.create_time > chatroom_create_time)
    filter_list_in.append(AContact.id > 0)
    filter_list_out = AMember.get_filter_list(chatroomname = chatroom.chatroomname, is_deleted = True)
    filter_list_out.append(AMember.update_time >= start_time)
    filter_list_out.append(AMember.update_time < end_time)
    filter_list_out.append(AContact.id > 0)
    members_in = db.session.query(func.count(AMember.id)) \
        .outerjoin(AContact, AMember.username == AContact.username) \
        .filter(*filter_list_in).first()[0] or 0
    members_out = db.session.query(func.count(AMember.id)) \
        .outerjoin(AContact, AMember.username == AContact.username) \
        .filter(*filter_list_out).first()[0] or 0
    chatroom_overview.member_change = members_in - members_out
    if save_flag:
        db.session.commit()
    chatroom_overview.generate_update_time()
    return chatroom_overview


def update_active_class(chatroom_overview, save_flag = False):
    if not isinstance(chatroom_overview, ChatroomOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(chatroom_overview))
        return chatroom_overview
    if chatroom_overview.speak_count > 1000\
            or chatroom_overview.active_count > 50\
            or chatroom_overview.active_rate > 0.9:
        chatroom_overview.active_class = 3
    elif chatroom_overview.speak_count > 500\
            or chatroom_overview.active_count > 30\
            or chatroom_overview.active_rate > 0.8:
        chatroom_overview.active_class = 2
    elif chatroom_overview.speak_count > 200\
            or chatroom_overview.active_count > 10\
            or chatroom_overview.active_rate > 0.6:
        chatroom_overview.active_class = 1
    else:
        chatroom_overview.active_class = 0
    if save_flag:
        db.session.commit()
    chatroom_overview.generate_update_time()
    return chatroom_overview


def batch_update_member_overview(member_overview, chatroom_create_time, save_flag = False):
    if not isinstance(member_overview, MemberOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(member_overview))
        return member_overview
    update_speak_count_and_be_at_count(member_overview, chatroom_create_time)
    update_invitation_count(member_overview, chatroom_create_time)
    update_effect_num(member_overview)
    if save_flag:
        db.session.commit()
    member_overview.generate_update_time()
    return member_overview


def update_speak_count_and_be_at_count(member_overview, chatroom_create_time, save_flag = False):
    if not isinstance(member_overview, MemberOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(member_overview))
        return member_overview
    if member_overview.scope == SCOPE_24_HOUR:
        end_time = datetime.now()
        start_time = end_time - timedelta(days = 1)
        # MessageAnalysis
        filter_list_ma = MessageAnalysis.get_filter_list(start_time = start_time, end_time = end_time)
        filter_list_ma.append(MessageAnalysis.real_talker == member_overview.username)
        filter_list_ma.append(MessageAnalysis.talker == member_overview.chatroomname)
        filter_list_ma.append(MessageAnalysis.type < MSG_TYPE_SYS)
        filter_list_ma.append(MessageAnalysis.create_time >= chatroom_create_time)
        speak_count = db.session.query(func.count(MessageAnalysis.msg_id))\
            .filter(*filter_list_ma).first()[0] or 0

        filter_list_ma = MessageAnalysis.get_filter_list(start_time = start_time, end_time = end_time)
        filter_list_ma.append(MessageAnalysis.member_id_be_at == member_overview.member_id)
        filter_list_ma.append(MessageAnalysis.talker == member_overview.chatroomname)
        filter_list_ma.append(MessageAnalysis.type == MSG_TYPE_TXT)
        filter_list_ma.append(MessageAnalysis.create_time >= chatroom_create_time)
        be_at_count = db.session.query(func.count(MessageAnalysis.msg_id))\
            .filter(*filter_list_ma).first()[0] or 0
    else:
        start_time, end_time = get_time_window_by_scope(scope = member_overview.scope)
        # MemberStatistics
        filter_list_ms = MemberStatistic.get_filter_list(member_id = member_overview.member_id,
                                                         chatroom_id = member_overview.chatroom_id,
                                                         start_time = start_time, end_time = end_time)
        speak_count = 0
        be_at_count = 0
        ms_list = db.session.query(MemberStatistic).filter(*filter_list_ms).all()
        for ms in ms_list:
            speak_count += ms.speak_count
            be_at_count += ms.be_at_count

    member_overview.speak_count = speak_count
    member_overview.be_at_count = be_at_count
    if save_flag:
        db.session.commit()
    member_overview.generate_update_time()
    return member_overview


def update_invitation_count(member_overview, chatroom_create_time, save_flag = False):
    if not isinstance(member_overview, MemberOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(member_overview))
        return member_overview
    if member_overview.scope == SCOPE_24_HOUR:
        end_time = datetime.now()
        start_time = end_time - timedelta(days = 1)
    else:
        start_time, end_time = get_time_window_by_scope(scope = member_overview.scope)
    # MemberInviteMember
    filter_list_mim = MemberInviteMember.get_filter_list(invitor_id = member_overview.member_id,
                                                         start_time = start_time, end_time = end_time)
    filter_list_mim.append(MemberInviteMember.create_time >= chatroom_create_time)
    invitation_count = db.session.query(func.count(distinct(MemberInviteMember.invited_id))) \
        .filter(*filter_list_mim).first()[0] or 0

    member_overview.invitation_count = invitation_count
    if save_flag:
        db.session.commit()
    member_overview.generate_update_time()
    return member_overview


def update_effect_num(member_overview, save_flag = False):
    if not isinstance(member_overview, MemberOverview):
        logger.error(u'batch_update_chatroom_overview: not a entity of ChatroomOverview')
        logger.error(u'type: ', type(member_overview))
        return member_overview
    if member_overview.speak_count > 100 or member_overview.be_at_count > 30 or member_overview.invitation_count > 10:
        member_overview.effect_num = 3
    elif member_overview.speak_count > 50 or member_overview.be_at_count > 10 or member_overview.invitation_count > 5:
        member_overview.effect_num = 2
    elif member_overview.speak_count > 20 or member_overview.be_at_count > 5 or member_overview.invitation_count > 2:
        member_overview.effect_num = 1
    else:
        member_overview.effect_num = 0
    if save_flag:
        db.session.commit()
    member_overview.generate_update_time()
    return member_overview
