# -*- coding: utf-8 -*-

import logging
from flask import request

from core.user_core import UserLogin
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from configs.config import SUCCESS, main_api, db, DEFAULT_PAGE, DEFAULT_PAGE_SIZE

logger = logging.getLogger('main')


@main_api.route('/member/get_member_list', methods=['POST'])
def member_get_member_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    page = request.json.get('page', DEFAULT_PAGE)
    page_size = request.json.get('page_size', DEFAULT_PAGE_SIZE)

    return make_response()


@main_api.route('/member/get_member_info', methods=['POST'])
def member_get_member_info():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    return make_response()
