# -*- coding: utf-8 -*-
import json

import time

from flask import request
from flask_uwsgi_websocket import GeventWebSocket

from configs.config import app, WS_MAP, main_api, SUCCESS, ERR_WRONG_ITEM, TASK_SEND_TYPE, db
from core.send_task_and_ws_setting_core import update_chatroom_members_info, update_members_info
from core.user_core import UserLogin
from models.chatroom_member_models import ChatroomInfo
from utils.u_model_json_str import verify_json
from utils.u_response import make_response

websocket = GeventWebSocket(app)


@websocket.route('/cia_api/cia_ws')
def echo(ws):
    with app.request_context(ws.environ), app.app_context():
        username = request.args.get('username')
        WS_MAP[username] = ws

        # threading_list = threading.enumerate()
        # for t in threading_list:
        #     if t.name == (u'bot_consumption' + username):
        #         t.stop()
        #         time.sleep(2)
        #         break
        # consumption_thread = ConsumptionThread(thread_id=(u'bot_consumption' + username))
        # consumption_thread.start()
        print 'username', username
        while True:
            msg = ws.receive()
            if msg:
                msg_json = json.loads(msg)
                if "ping" in msg_json.keys():
                    text_json = dict()
                    text_json['pong'] = int(time.time() * 1000)
                    text = json.dumps(text_json)
                    # print 'text', text
                    ws.send(text)
                    continue
                print 'msg', msg
                text_json = dict()
                text_json['username'] = "wxid_u391xytt57gc21"
                text_json['content'] = "是小智呀"
                text_json['type'] = TASK_SEND_TYPE['text']
                text = json.dumps(text_json)
                ws.send(text)
                print 'text', text
            if not ws.connected:
                # TODO-zwf 退出逻辑待完善
                print 'ws.connected', str(ws.connected)
                print 'quit'
                WS_MAP.pop(username)
                break
        # consumption_thread.stop()


@main_api.route('/websocket/update_chatroom_members_info', methods=['POST'])
def websocket_update_chatroom_members_info():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    chatroom_id = request.json.get('chatroom_id')
    if not chatroom_id:
        return make_response(ERR_WRONG_ITEM)
    chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroom_id == chatroom_id).first()
    if not chatroom:
        return make_response(ERR_WRONG_ITEM)
    update_chatroom_members_info(chatroom.chatroomname)

    return make_response(SUCCESS)


@main_api.route('/websocket/update_members_info', methods=['POST'])
def websocket_update_members_info():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    member_usernames = request.json.get('member_usernames')
    if not member_usernames:
        return make_response(ERR_WRONG_ITEM)

    update_members_info(member_usernames = member_usernames)

    return make_response(SUCCESS)
