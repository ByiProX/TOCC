# -*- coding: utf-8 -*-
import json
import threading

import time
from flask import request
from flask_uwsgi_websocket import GeventWebSocket

from configs.config import app, WS_MAP
from core.consumption_core import ConsumptionThread

websocket = GeventWebSocket(app)


@websocket.route('/yaca_api/yaca_ws')
def echo(ws):
    with app.request_context(ws.environ), app.app_context():
        username = request.args.get('username')
        WS_MAP[username] = ws

        threading_list = threading.enumerate()
        for t in threading_list:
            if t.name == (u'bot_consumption' + username):
                t.stop()
                time.sleep(2)
                break
        consumption_thread = ConsumptionThread(thread_id=(u'bot_consumption' + username))
        consumption_thread.start()
        print 'username', username
        while True:
            msg = ws.receive()
            if msg:
                print 'msg', msg
                text_json = dict()
                text_json['username'] = "wxid_u391xytt57gc21"
                text_json['content'] = "是小智呀"
                text = json.dumps(text_json)
                print 'text', text
                ws.send(text)
            if not ws.connected:
                # TODO-zwf 退出逻辑待完善
                print 'ws.connected', str(ws.connected)
                print 'quit'
                WS_MAP.pop(username)
                break
        consumption_thread.stop()
