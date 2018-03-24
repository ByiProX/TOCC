# -*- coding: utf-8 -*-

import logging
import threading
import time
from copy import copy

from datetime import datetime, timedelta
from flask import request
from sqlalchemy import func

from core.send_task_and_ws_setting_core import check_chatroom_members_info
from core.user_core import UserLogin
from models.android_db_models import AMember, AContact
from models.chatroom_member_models import MemberInfo, MemberOverview, MemberInviteMember, MemberAtMember, ChatroomInfo
from models.message_ext_models import MessageAnalysis
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from configs.config import SUCCESS, main_api, db, DEFAULT_PAGE, DEFAULT_PAGE_SIZE, ERR_INVALID_PARAMS, \
    ERR_INVALID_MEMBER, ERR_WRONG_ITEM
from utils.u_time import datetime_to_timestamp_utc_8

logger = logging.getLogger('main')


@main_api.route('/member/get_member_list', methods=['POST'])
def member_get_member_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    scope = request.json.get('scope', 0)
    order = request.json.get('order', 1)
    page = request.json.get('page', DEFAULT_PAGE)
    page_size = request.json.get('page_size', DEFAULT_PAGE_SIZE)

    chatroom_id = request.json.get('chatroom_id')
    if not chatroom_id:
        return make_response(ERR_INVALID_PARAMS)
    chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroom_id == chatroom_id).first()
    if not chatroom:
        return make_response(ERR_INVALID_PARAMS)

    # Mark
    # 被删除成员是否要显示出来
    # AContact 可能不存在
    # AContact 信息可能下载不下来
    member_order_list = [MemberOverview.member_id.asc(),
                         MemberOverview.effect_num.desc(),
                         MemberOverview.speak_count.desc(),
                         MemberOverview.be_at_count.desc(),
                         MemberOverview.invitation_count.desc(),
                         MemberOverview.invitation_count.asc(),
                         MemberOverview.be_at_count.asc(),
                         MemberOverview.speak_count.asc(),
                         MemberOverview.effect_num.asc()]

    member_order = [member_order_list[order]]
    member_order += [MemberOverview.member_id.asc()]

    rows = db.session.query(MemberOverview, MemberInfo, AMember, AContact) \
        .filter(MemberOverview.chatroom_id == chatroom_id,
                MemberOverview.scope == scope)\
        .outerjoin(MemberInfo, MemberOverview.member_id == MemberInfo.member_id) \
        .outerjoin(AMember, MemberInfo.member_id == AMember.id) \
        .outerjoin(AContact, MemberInfo.username == AContact.username) \
        .filter(MemberOverview.chatroom_id == chatroom_id,
                MemberOverview.scope == scope,
                AContact.id > 0
                )\
        .order_by(*member_order)\
        .limit(page_size)\
        .offset(page * page_size)\
        .all()

    last_update_time = time.time() * 1000
    member_json_list = list()
    for row in rows:
        member_overview = row[0]
        member_info = row[1]
        a_member = row[2]
        a_contact = row[3]
        member_json = dict()
        member_json.update(a_contact.to_json())
        member_json.update(a_member.to_json())
        member_json.update(member_info.to_json())
        member_json.update(member_overview.to_json())
        member_json_list.append(member_json)
        last_update_time = datetime_to_timestamp_utc_8(member_overview.update_time)

    if page == 0:
        check_thread = threading.Thread(target = check_chatroom_members_info, args = (copy(chatroom.chatroomname), ))
        check_thread.setDaemon(True)
        check_thread.start()

    return make_response(SUCCESS, member_list = member_json_list, last_update_time = last_update_time)


@main_api.route('/member/get_member_info', methods=['POST'])
def member_get_member_info():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    member_id = request.json.get('member_id')
    if not member_id:
        return make_response(ERR_INVALID_PARAMS)

    # row = db.session.query(MemberInfo, AMember, AContact) \
    #     .outerjoin(AMember, MemberInfo.chatroom_id == AMember.id) \
    #     .outerjoin(AContact, MemberInfo.username == AContact.username) \
    #     .filter(MemberInfo)\
    #     .all()
    member_info = db.session.query(MemberInfo).filter(MemberInfo.member_id == member_id).first()
    if not member_info:
        return make_response(ERR_INVALID_MEMBER)
    a_member = db.session.query(AMember).filter(AMember.id == member_id).first()
    a_contact = db.session.query(AContact).filter(AContact.username == member_info.username).first()
    if not a_contact:
        return make_response(ERR_WRONG_ITEM)
    member_json = dict()
    member_json.update(a_contact.to_json())
    member_json.update(a_member.to_json())
    member_json.update(member_info.to_json())

    return make_response(SUCCESS, member_info = member_json)


@main_api.route('/member/get_invitation_list', methods=['POST'])
def member_get_invitation_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # page = request.json.get('page', DEFAULT_PAGE)
    # page_size = request.json.get('page_size', DEFAULT_PAGE_SIZE)
    member_id = request.json.get('member_id')
    if not member_id:
        return make_response(ERR_INVALID_PARAMS)

    invitation_list = list()
    filter_list_mim = MemberInviteMember.get_filter_list(invitor_id = member_id)
    total_num = db.session.query(func.count(MemberInviteMember.invited_id)).filter(*filter_list_mim).first()[0] or 0
    mim_list = db.session.query(MemberInviteMember, AContact)\
        .outerjoin(AContact, MemberInviteMember.invited_username == AContact.username) \
        .filter(*filter_list_mim).order_by(MemberInviteMember.create_time.desc())\
        .all()
    # .limit(page_size).offset(page * page_size)\

    for row in mim_list:
        mim = row[0]
        a_contact = row[1]
        member_json = dict()
        member_json['member_id'] = mim.invited_id
        member_json['create_time'] = datetime_to_timestamp_utc_8(mim.create_time)
        member_json['nickname'] = ""
        member_json['avatar_url2'] = ""
        if a_contact:
            member_json['nickname'] = a_contact.nickname
            member_json['avatar_url2'] = a_contact.avatar_url2
        invitation_list.append(member_json)

    return make_response(SUCCESS, invitation_list = invitation_list, total_num = total_num)


@main_api.route('/member/get_at_list', methods=['POST'])
def member_get_at_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    limit = 3
    member_id = request.json.get('member_id')
    if not member_id:
        return make_response(ERR_INVALID_PARAMS)

    filter_list_mam = MemberAtMember.get_filter_list(to_member_id = member_id)
    mam_list = db.session.query(func.count(MemberAtMember.create_time), AContact)\
        .outerjoin(MemberInfo, MemberAtMember.from_member_id == MemberInfo.member_id) \
        .outerjoin(AContact, MemberInfo.username == AContact.username)\
        .filter(*filter_list_mam)\
        .group_by(MemberAtMember.from_username)\
        .order_by(func.count(MemberAtMember.create_time))\
        .limit(limit)\
        .all()

    member_list = list()
    for row in mam_list:
        at_count = row[0]
        a_contact = row[1]
        member_json = dict()
        member_json.update(a_contact.to_json())
        member_json['at_count'] = at_count
        member_list.append(member_json)

    return make_response(SUCCESS, member_list = member_list)


@main_api.route('/member/get_active_period', methods=['POST'])
def member_get_active_period():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    chatroom_id = request.json.get('chatroom_id')
    member_id = request.json.get('member_id')
    if not member_id:
        return make_response(ERR_INVALID_PARAMS)
    if not chatroom_id:
        return make_response(ERR_INVALID_PARAMS)
    member = db.session.query(MemberInfo).filter(MemberInfo.member_id == member_id).first()
    if not member:
        return make_response(ERR_WRONG_ITEM)

    active_period_list = [0] * 24
    now = datetime.now()
    filter_list_msg = MessageAnalysis.get_filter_list(start_time = now - timedelta(days = 7), end_time = now,
                                                      is_to_friend = False)
    filter_list_msg.append(MessageAnalysis.real_talker == member.username)
    filter_list_msg.append(MessageAnalysis.talker == member.chatroomname)
    msg_list = db.session.query(MessageAnalysis).filter(*filter_list_msg).all()

    for msg in msg_list:
        active_period_list[msg.create_time.hour] += 1

    return make_response(SUCCESS, active_period_list = active_period_list)
