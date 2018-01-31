# -*- coding: utf-8 -*-
from flask import jsonify

from config import ERROR_CODE


def make_response(*args, **kwargs):
    status = args[0]

    # a default json
    response_body = jsonify({'err_code': ERROR_CODE[status['status_code']], 'content': kwargs})

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

    response_body.headers['Access-Control-Allow-Origin'] = '*'
    # response_body.headers['Access-Control-Allow-Credentials'] = 'true'
    # response_body.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    # response_body.headers['Access-Control-Allow-Headers'] = 'X-Custom-Header'
    return response_body
