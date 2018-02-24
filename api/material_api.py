# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, ERR_PARAM_SET, main_api
from core.user_core import UserLogin
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api.route('/get_material_list', methods=['POST'])
def app_get_material_list():
    """
    读取该用户的某种资源
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    material_type = request.json.get('material_type')
    if not material_type:
        return make_response(ERR_PARAM_SET)

    raise NotImplementedError


@main_api.route('/upload_file', methods=['POST'])
def app_download_file_from_frontend():
    """
    从前端传过来的文件，存在cdn上
    :return:
    """
    download_file = request.files['file']

    # 确认图片是否在cdn上，如果在，则不进行上传，直接进行cdn与ml的绑定
    # 如果不在，则先上传至cdn，然后将文件与ml绑定


def _send_file_into_cdn():
    """
    将图片存入cdn
    :return:
    """


def _get_file_from_cdn():
    """
    从cdn读取内容
    :return:
    """
