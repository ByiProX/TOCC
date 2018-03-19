# -*- coding: utf-8 -*-

import logging
from flask import request
from sqlalchemy import func, and_

from core.user_core import UserLogin
from models.android_db_models import AContact, AMember
from models.chatroom_member_models import ChatroomInfo, UserChatroomR, ChatroomOverview, ChatroomStatistic, \
    ChatroomActive
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from configs.config import SUCCESS, main_api, db, DEFAULT_PAGE, DEFAULT_PAGE_SIZE, ERR_INVALID_PARAMS, ERR_WRONG_ITEM, \
    SCOPE_WEEK
from utils.u_time import get_time_window_by_scope, datetime_to_timestamp_utc_8

logger = logging.getLogger('main')


@main_api.route('/chatroom/get_chatroom_list', methods = ['POST'])
def chatroom_get_chatroom_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    scope = request.json.get('scope', 0)
    page = request.json.get('page', DEFAULT_PAGE)
    page_size = request.json.get('page_size', DEFAULT_PAGE_SIZE)

    order = [ChatroomOverview.speak_count.desc(), ChatroomOverview.chatroom_id.asc()]

    chatroom_overview_list = db.session.query(ChatroomOverview) \
        .outerjoin(UserChatroomR, UserChatroomR.chatroom_id == ChatroomOverview.chatroom_id) \
        .filter(UserChatroomR.user_id == user_info.user_id,
                ChatroomOverview.scope == scope) \
        .order_by(*order).limit(page_size).offset(page * page_size)\
        .all()

    chatroom_ids_in_order = [r.chatroom_id for r in chatroom_overview_list]

    rows = db.session.query(ChatroomInfo, AContact).outerjoin(AContact, ChatroomInfo.chatroom_id == AContact.id) \
        .filter(ChatroomInfo.chatroom_id.in_(chatroom_ids_in_order)).all()

    chatroom_json_dict = dict()
    for row in rows:
        chatroom_json = dict()
        chatroom = row[0]
        a_contact_chatroom = row[1]
        chatroom_json.update(a_contact_chatroom.to_json())
        chatroom_json.update(chatroom.to_json())
        chatroom_json_dict[chatroom.chatroom_id] = chatroom_json

    chatroom_json_list = list()
    for chatroom_overview in chatroom_overview_list:
        chatroom_json = chatroom_json_dict[chatroom_overview.chatroom_id]
        chatroom_json.update(chatroom_overview.to_json())
        chatroom_json_list.append(chatroom_json)

    return make_response(SUCCESS, chatroom_list = chatroom_json_list)


@main_api.route('/chatroom/get_chatroom_info', methods = ['POST'])
def chatroom_get_chatroom_info():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    chatroom_id = request.json.get('chatroom_id')
    if not chatroom_id:
        return make_response(ERR_INVALID_PARAMS)
    chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroom_id == chatroom_id).first()
    if not chatroom:
        return make_response(ERR_WRONG_ITEM)
    a_contact_chatroom = db.session.query(AContact).filter(AContact.id == chatroom.chatroom_id).first()
    chatroom_json = chatroom.to_json()
    a_contact_chatroom_json = a_contact_chatroom.to_json()
    a_contact_chatroom_json.update(chatroom_json)

    return make_response(SUCCESS, chatroom_info = a_contact_chatroom_json)


@main_api.route('/chatroom/get_chatroom_tendency', methods=['POST'])
def chatroom_get_msg_tendency():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    scope = request.json.get('scope', SCOPE_WEEK)
    chatroom_id = request.json.get("chatroom_id")
    if not chatroom_id:
        return make_response(ERR_INVALID_PARAMS)

    start_time, end_time = get_time_window_by_scope(scope = scope)
    cs_list = db.session.query(ChatroomStatistic)\
        .filter(ChatroomStatistic.chatroom_id == chatroom_id,
                ChatroomStatistic.time_to_day >= start_time,
                ChatroomStatistic.time_to_day < end_time)\
        .order_by(ChatroomStatistic.time_to_day.asc()).all()

    msg_tendency = [0] * (scope - len(cs_list))
    in_count = [0] * (scope - len(cs_list))
    out_count = [0] * (scope - len(cs_list))
    total_count = [0] * (scope - len(cs_list))
    for cs in cs_list:
        msg_tendency.append(cs.speak_count)
        in_count.append(cs.in_count)
        out_count.append(cs.out_count)
        total_count.append(cs.member_count)

    return make_response(SUCCESS, msg_count_list = msg_tendency, in_count = in_count, out_count = out_count,
                         total_count = total_count)


@main_api.route('/chatroom/get_active_tendency', methods=['POST'])
def chatroom_get_active_tendency():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    scope = request.json.get('scope', SCOPE_WEEK)
    chatroom_id = request.json.get("chatroom_id")
    if not chatroom_id:
        return make_response(ERR_INVALID_PARAMS)

    start_time, end_time = get_time_window_by_scope(scope = scope)
    rows = db.session.query(func.count(ChatroomActive.member_id), ChatroomStatistic.member_count)\
        .outerjoin(ChatroomStatistic, and_(ChatroomActive.chatroom_id == ChatroomStatistic.chatroom_id)) \
        .filter(ChatroomActive.chatroom_id == chatroom_id,
                ChatroomActive.time_to_day >= start_time,
                ChatroomActive.time_to_day < end_time).group_by(ChatroomActive.time_to_day).all()

    print rows

    active_count_list = [0] * (scope - len(rows))
    for row in rows:
        active_count = row[0]
        active_count_list.append(active_count)

    return make_response(SUCCESS, active_count_list = active_count_list)


@main_api.route('/chatroom/get_in_out_members', methods=['POST'])
def chatroom_get_in_out_members():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    page = request.json.get('page', DEFAULT_PAGE)
    page_size = request.json.get('page_size', DEFAULT_PAGE_SIZE)
    chatroom_id = request.json.get("chatroom_id")
    if not chatroom_id:
        return make_response(ERR_INVALID_PARAMS)

    chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroom_id == chatroom_id).first()
    if not chatroom:
        return make_response(ERR_WRONG_ITEM)
    chatroomname = chatroom.chatroomname
    chatroom_create_time = chatroom.create_time

    in_list = list()
    out_list = list()
    filter_list_in = AMember.get_filter_list(chatroomname = chatroomname, is_deleted = False)
    filter_list_in.append(AMember.create_time > chatroom_create_time)
    filter_list_out = AMember.get_filter_list(chatroomname = chatroomname, is_deleted = True)
    members_in_query = db.session.query(AMember, AContact).outerjoin(AContact, AMember.username == AContact.username)\
        .filter(*filter_list_in)
    members_in = members_in_query.order_by(AMember.create_time.desc()).limit(page_size).offset(page * page_size).all()
    for row in members_in:
        a_member = row[0]
        a_contact = row[1]
        member_json = dict()
        member_json['member_id'] = a_member.id
        member_json['nickname'] = a_contact.nickname
        member_json['avatar_url'] = a_contact.avatar_url2
        member_json['create_time'] = datetime_to_timestamp_utc_8(a_member.create_time)
        in_list.append(member_json)
    members_out_query = db.session.query(AMember, AContact).outerjoin(AContact, AMember.username == AContact.username)\
        .filter(*filter_list_out)
    members_out = members_out_query.order_by(AMember.create_time.desc()).limit(page_size).offset(page * page_size).all()
    for row in members_out:
        a_member = row[0]
        a_contact = row[1]
        member_json = dict()
        member_json['member_id'] = a_member.id
        member_json['nickname'] = a_contact.nickname
        member_json['avatar_url'] = a_contact.avatar_url2
        member_json['update_time'] = datetime_to_timestamp_utc_8(a_member.update_time)
        out_list.append(member_json)

    return make_response(SUCCESS, in_list = in_list, out_list = out_list)
