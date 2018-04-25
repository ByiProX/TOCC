# -*- coding: utf-8 -*-
import time

from flask import request
from configs.config import main_api_v2
from core_v2.user_core import UserLogin
from models_v2.base_model import *
from utils.z_utils import para_check, response, true_false_to_10, _10_to_true_false
from utils.u_time import datetime_to_timestamp_utc_8, get_today_0


@main_api_v2.route('/sensitive_rule', methods=['POST'])
@para_check("token", "chatroom_name_list", "sensitive_word_list")
def create_or_modify_sensitive_rule():
    # Check owner or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})

    if request.json.get('rule_id') is not None:
        # Modify rule.
        rule_id = request.json.get('rule_id')
        # Get a available previous rule by its id.
        previous_rule = BaseModel.fetch_by_id('sensitive_message_rule', rule_id)
        if previous_rule is None:
            return response({'err_code': -3, 'err_info': 'Can not find this rule by its id.'})
        # Modify this rule.
        value_as_dict = request.json
        previous_rule.chatroom_name_list = value_as_dict["chatroom_name_list"]
        previous_rule.sensitive_word_list = value_as_dict["sensitive_word_list"]
        previous_rule.owner_list = [owner, ]
        previous_rule.save()
        modified_rule = BaseModel.fetch_by_id('sensitive_message_rule', rule_id)
        modified_rule_result = {
            'rule_id': rule_id,
            'chatroom_name_list': modified_rule.chatroom_name_list,
            'sensitive_word_list': modified_rule.sensitive_word_list,
            'owner_list': modified_rule.owner_list,
            'is_work': modified_rule.is_work
        }
        return response({'err_code': 0, 'content': _10_to_true_false(modified_rule_result)})
    else:
        # Create rule.
        new_rule = CM('sensitive_message_rule')
        value_as_dict = request.json
        new_rule.chatroom_name_list = value_as_dict["chatroom_name_list"]
        new_rule.sensitive_word_list = value_as_dict["sensitive_word_list"]
        new_rule.owner_list = [owner, ]
        new_rule.is_work = 1
        new_rule.save()
        created_rule = BaseModel.fetch_by_id('sensitive_message_rule', new_rule.sensitive_message_rule_id)
        created_rule_result = {
            'rule_id': new_rule.sensitive_message_rule_id,
            'chatroom_name_list': created_rule.chatroom_name_list,
            'sensitive_word_list': created_rule.sensitive_word_list,
            'owner_list': created_rule.owner_list,
            'is_work': created_rule.is_work
        }
        return response({'err_code': 0, 'content': _10_to_true_false(created_rule_result)})


@main_api_v2.route('/sensitive_rule_delete', methods=['POST'])
@para_check("token", "rule_id", )
def sensitive_rule_delete():
    rule_id = request.json.get('rule_id')
    this_rule = BaseModel.fetch_by_id('sensitive_message_rule', rule_id)
    if this_rule is None:
        return response({'err_code': -3, 'err_info': 'rule_id wrong.'})
    this_rule.is_work = 0
    this_rule.save()
    this_rule_result = {
        'rule_id': this_rule.sensitive_message_rule_id,
        'chatroom_name_list': this_rule.chatroom_name_list,
        'sensitive_word_list': this_rule.sensitive_word_list,
        'owner_list': this_rule.owner_list,
        'is_work': this_rule.is_work
    }
    return response({'err_code': 0, 'content': _10_to_true_false(this_rule_result)})


@main_api_v2.route('/sensitive_rule_list', methods=['POST'])
@para_check("token", )
def sensitive_rule_list():
    # Check owner or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})

    all_rule_list = BaseModel.fetch_all('sensitive_message_rule', '*', BaseModel.where_dict({'is_work': 1}))
    this_owner_rule_list = []
    content = []

    for rule in all_rule_list:
        if owner in rule.owner_list:
            this_owner_rule_list.append(rule)

    for rule in this_owner_rule_list:
        rule_id = rule.sensitive_message_rule_id
        # Create chatroom_list
        chatroom_list = []
        for chatroomname in rule.chatroom_name_list:
            this_chatroom = BaseModel.fetch_one('a_chatroom', '*', BaseModel.where_dict({'chatroomname': chatroomname}))
            if this_chatroom is None:
                return response({'err_code': -3, 'err_info': 'Invalid chatroomname:%s' % chatroomname})
            avatar_url = this_chatroom.avatar_url
            nickname = this_chatroom.nickname_real
            chatroom_list.append(
                {'avatar_url': avatar_url, 'chatroomname': chatroomname, 'chatroom_nickname': nickname})

        sensitive_word_list = rule.sensitive_word_list
        content.append({'rule_id': rule_id, 'chatroom_list': chatroom_list, 'sensitive_word_list': sensitive_word_list})

    return response({'err_code': 0, 'content': content})


@main_api_v2.route('/sensitive_message_log', methods=['POST'])
@para_check("token", "date_type", "page", "pagesize")
def sensitive_message_log():
    now = int(time.time())
    date_type = int(request.json.get('date_type'))
    page = int(request.json.get('page'))
    pagesize = int(request.json.get('pagesize'))

    """
    date_type
    -> 1 今天
    -> 2 昨天
    -> 3 近7天
    -> 4 近30天
    -> 5 全部
    """
    cur_time = time.time()
    today_start = int(cur_time - cur_time % 86400)
    yesterday_start = int(cur_time - cur_time % 86400 - 86400)
    seven_before = int(cur_time - cur_time % 86400 - 86400 * 6)
    thirty_before = int(cur_time - cur_time % 86400 - 86400 * 29)

    time_dict = {
        1: (today_start, now),
        2: (yesterday_start, today_start),
        3: (seven_before, now),
        4: (thirty_before, now),
        5: (0, now)
    }

    time_limit = time_dict[date_type]

    all_log_list = BaseModel.fetch_all('sensitive_message_log', '*',
                                       BaseModel.and_(BaseModel.where(">", "create_time", time_limit[0]),
                                                      BaseModel.where("<", "create_time", time_limit[1])), page=page,
                                       pagesize=pagesize)

    for log in all_log_list:
        print(log)

    return '666'
