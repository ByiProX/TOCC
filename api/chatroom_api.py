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

    page = request.json.get('page', DEFAULT_PAGE)
    page_size = request.json.get('page_size', DEFAULT_PAGE_SIZE)

    order = ChatroomOverview.speak_count.desc()

    chatroom_ids_row = db.session.query(UserChatroomR.chatroom_id) \
        .outerjoin(ChatroomOverview, UserChatroomR.chatroom_id == ChatroomOverview.chatroom_id) \
        .filter(UserChatroomR.user_id == user_info.user_id) \
        .order_by(order).limit(page_size).offset(page * page_size).all()

    chatroom_ids = [r[0] for r in chatroom_ids_row]

    rows = db.session.query(ChatroomInfo, AContact).outerjoin(AContact, ChatroomInfo.chatroom_id == AContact.id) \
        .filter(ChatroomInfo.chatroom_id.in_(chatroom_ids)).all()

    chatroom_json_list = list()
    for row in rows:
        chatroom_json = dict()
        chatroom = row[0]
        a_contact_chatroom = row[1]
        chatroom_json.update(a_contact_chatroom.to_json())
        chatroom_json.update(chatroom.to_json())
        chatroom_json_list.append(chatroom_json)

    return make_response(SUCCESS, chatroom_json_list = chatroom_json_list)


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
