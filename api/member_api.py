# -*- coding: utf-8 -*-

import logging

from datetime import datetime
from flask import request
from sqlalchemy import func

from core.user_core import UserLogin
from models.android_db_models import AMember, AContact
from models.chatroom_member_models import MemberInfo, MemberOverview, MemberInviteMember
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
    page = request.json.get('page', DEFAULT_PAGE)
    page_size = request.json.get('page_size', DEFAULT_PAGE_SIZE)

    chatroom_id = request.json.get('chatroom_id')
    if not chatroom_id:
        return make_response(ERR_INVALID_PARAMS)

    # Mark
    # 被删除成员是否要显示出来
    # AContact 可能不存在
    # AContact 信息可能下载不下来
    order = [MemberOverview.speak_count.desc(), MemberOverview.member_id.asc()]
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
        .order_by(*order)\
        .limit(page_size)\
        .offset(page * page_size)\
        .all()

    last_update_time = datetime.now()
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

    page = request.json.get('page', DEFAULT_PAGE)
    page_size = request.json.get('page', DEFAULT_PAGE_SIZE)
    member_id = request.json.get('member_id')
    if not member_id:
        return make_response(ERR_INVALID_PARAMS)

    invitation_list = list()
    filter_list_mim = MemberInviteMember.get_filter_list(invitor_id = member_id)
    total_num = db.session.query(func.count(MemberInviteMember.invited_id)).filter(*filter_list_mim).first()[0] or 0
    mim_list = db.session.query(MemberInviteMember, AContact)\
        .outerjoin(AContact, MemberInviteMember.invited_username == AContact.username) \
        .filter(*filter_list_mim).order_by(MemberInviteMember.create_time.desc())\
        .limit(page_size).offset(page * page_size).all()

    for row in mim_list:
        mim = row[0]
        a_contact = row[1]
        member_json = dict()
        member_json['member_id'] = mim.invited_id
        member_json['create_time'] = datetime_to_timestamp_utc_8(mim.create_time)
        member_json['nickname'] = ""
        member_json['avatar_url2'] = ""
        if not a_contact:
            member_json['nickname'] = a_contact.nickname
            member_json['avatar_url2'] = a_contact.avatar_url2
        invitation_list.append(member_json)

    return make_response(SUCCESS, invitation_list = invitation_list, total_num = total_num)
