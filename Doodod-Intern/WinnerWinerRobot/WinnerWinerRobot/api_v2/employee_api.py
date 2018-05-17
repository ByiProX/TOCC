# -*- coding: utf-8 -*-
import time
import threading

from flask import request

from configs.config import main_api_v2
from core_v2.user_core import UserLogin
from models_v2.base_model import *
from utils.z_utils import para_check, response, true_false_to_10, _10_to_true_false


@main_api_v2.route('/employee_search', methods=["POST"])
@para_check('keyword', )
def employee_search():
    try:
        keyword = unicode(request.json.get('keyword'))
        if keyword == "":
            return response({'err_code': -1, 'err_info': 'keyword could not be blank!'})
        user_list = BaseModel.fetch_all('a_contact', '*', BaseModel.or_(['=', 'alias', keyword],
                                                                        ['=', 'username', keyword],
                                                                        ['=', 'quan_pin', keyword],
                                                                        ['=', 'nickname', keyword], ), pagesize=100,
                                        page=1)
        result = []
        for i in user_list:
            _result = i.to_json_full()
            result.append({'username': _result.get('username'), 'nickname': _result.get('nickname'),
                           'avatar_url': _result.get('avatar_url')})
    except Exception as e:
        return response({'err_code': -1, 'err_info': '%s' % e})
    return response({'err_code': 0, 'content': result})
