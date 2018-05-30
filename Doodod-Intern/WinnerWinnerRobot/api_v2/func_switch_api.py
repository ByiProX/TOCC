# -*- coding: utf-8 -*-
import time
import threading

from flask import request

from configs.config import main_api_v2, ANDROID_SERVER_URL_BOT_STATUS, ANDROID_SERVER_URL_SEND_MESSAGE
from core_v2.user_core import UserLogin, _get_a_balanced_bot, _get_qr_code_base64_str
from models_v2.base_model import *
from utils.z_utils import *
from utils.tag_handle import Tag


@main_api_v2.route('/_func', methods=["POST"])
def test():
    all_client_list = BaseModel.fetch_all('client_member', '*', BaseModel.where_dict({'func_switch': None}))

    for client in all_client_list:
        client.func_switch = Tag().load_config(client.app).as_int()
        client.save()
        print(Tag().load_config(client.app).as_int())

    return ''
