# -*- coding: utf-8 -*-
import json

from flask import request
from flask_uwsgi_websocket import GeventWebSocket

from configs.config import app, WS_MAP
from core.consumption_core import ConsumptionThread

websocket = GeventWebSocket(app)


@websocket.route('/api/wwr_ws')
def echo(ws):
    with app.request_context(ws.environ), app.app_context():
        username = request.args.get('username')
        WS_MAP[username] = ws
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
            # TODO-zc 当状态异常时，跳出循环
            if not ws:
                break
        consumption_thread.stop()
