# -*- coding: utf-8 -*-

from flask import request
from configs.config import main_api_v2
from core_v2.user_core import UserLogin
from models_v2.base_model import *
from utils.z_utils import para_check, response, true_false_to_10, _10_to_true_false


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
        previous_rule = BaseModel.fetch_by_id('sensitive_message_rule', rule_id)
        if previous_rule is None:
            return response({'err_code': -3, 'err_info': 'Can not find this rule by its id.'})
        # Get a available previous rule by its id.
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
        return response(_10_to_true_false(modified_rule_result))
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
        return response(_10_to_true_false(created_rule_result))


@main_api_v2.route('/sensitive_rule_delete', methods=['POST'])
def sensitive_rule_delete():
    pass


@main_api_v2.route('/sensitive_rule_list', methods=['POST'])
def sensitive_rule_list():
    pass


@main_api_v2.route('/sensitive_message_log', methods=['POST'])
def sensitive_message_log():
    pass
