# -*- coding: utf-8 -*-
from flask import request
from flask_uwsgi_websocket import GeventWebSocket

from configs.config import app, ws_map

websocket = GeventWebSocket(app)


@websocket.route('/api/wwr_ws')
def echo(ws):
    with app.request_context(ws.environ), app.app_context():
        username = request.args.get('username')
        ws_map[username] = ws
        # while True:
        #     msg = ws.receive()
        #     ws.send(msg)
