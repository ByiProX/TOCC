# -*- coding: utf-8 -*-

import logging
from flask import request

from core.user_core import UserLogin
from models.android_db_models import AContact
from models.chatroom_member_models import ChatroomInfo, UserChatroomR, ChatroomOverview
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from configs.config import SUCCESS, main_api, db, DEFAULT_PAGE, DEFAULT_PAGE_SIZE

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
    chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroom_id == chatroom_id).first()
    a_contact_chatroom = db.session.query(AContact).filter(AContact.id == chatroom.chatroom_id).first()
    chatroom_json = chatroom.to_json()
    a_contact_chatroom_json = a_contact_chatroom.to_json()
    a_contact_chatroom_json.update(chatroom_json)

    return make_response(SUCCESS, chatroom_info = a_contact_chatroom_json)
