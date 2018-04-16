# -*- coding: utf-8 -*-

import logging

import time
from flask import request

from configs.config import main_api_v2, SUCCESS
from models_v2.base_model import BaseModel
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api_v2.route("/script", methods = ['POST'])
def script():
    uqr = BaseModel.fetch_by_id("client_qun_r", "5ad46153f5d7e26589658ba7")
    uqr.group_id = u"4_0"
    uqr.update()
    return make_response(SUCCESS)
