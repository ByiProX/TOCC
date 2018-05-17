# -*- coding: utf-8 -*-
from flask import request

from configs.config import SUCCESS
from core.user_core import UserLogin
from utils.u_response import make_response


# def app_get_batch_sending_task():
#     """
#     得到主界面所需的所有信息
#     :return:
#     """
#     status, user_info = UserLogin.verify_token(request.json.get('token'))
#     if status != SUCCESS:
#         return make_response(status)
