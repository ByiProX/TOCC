# -*- coding: utf-8 -*-

import logging
from flask import request

from core.user_core import UserLogin
from models.android_db_models import AMember, AContact
from models.chatroom_member_models import MemberInfo, MemberOverview
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from configs.config import SUCCESS, main_api, db, DEFAULT_PAGE, DEFAULT_PAGE_SIZE, ERR_INVALID_PARAMS, \
    ERR_INVALID_MEMBER

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
                # AContact.nickname > ""
                )\
        .order_by(*order)\
        .limit(page_size)\
        .offset(page * page_size)\
        .all()

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

    return make_response(SUCCESS, member_list = member_json_list)


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
    member_json = dict()
    member_json.update(a_contact.to_json())
    member_json.update(a_member.to_json())
    member_json.update(member_info.to_json())

    return make_response(SUCCESS, member_info = member_json)
