# -*- coding: utf-8 -*-
from flask import jsonify, request

from configs.config import ERROR_CODE, app


def make_response(*args, **kwargs):
    with app.app_context():
        # print request.headers
        status = args[0]

        # a default json
        response_body = jsonify({'err_code': ERROR_CODE[status]['status_code'], 'content': kwargs})

        # if status == LOGIN_SUCCESS_STATUS:
        #     token = args[2]
        #     response_body = jsonify({'err_code': 0, 'content': {'msg': status, 'token': token}})
        #
        # if status == LOGIN_FAILED_STATUS:
        #     response_body = jsonify({'err_code': 1, 'content': {'msg': status}})
        #
        # if status == UNAUTH_STATUS:
        #     response_body = jsonify({'err_code': 1, 'content': {'msg': status}})
        #
        # if status == REGIST_SUCCESS_STATUS:
        #     response_body = jsonify({'err_code': 0, 'content': {'msg': status}})

        # origin_2 = ('Access-Control-Allow-Origin', 'http://test.xuanren360.com')
        print request.headers.get("Origin")
        if "test.xuanren.com" in request.headers.get("Origin"):
            response_body.headers['Access-Control-Allow-Origin'] = 'http://test.xuanren360.com'
        # response_body.headers['Access-Control-Allow-Credentials'] = 'true'
        # response_body.headers['Access-Control-Allow-Methods'] = 'GET, POST'
        # response_body.headers['Access-Control-Allow-Headers'] = 'X-Custom-Header'
        return response_body
