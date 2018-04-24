# -*- coding: utf-8 -*-


from configs.config import main_api_v2
from core_v2.user_core import UserLogin
from models_v2.base_model import *
from utils.z_utils import para_check


@main_api_v2.route('/sensitive_rule', methods=['POST'])
def create_or_modify_sensitive_rule():
    pass


@main_api_v2.route('/sensitive_rule_delete', methods=['POST'])
def sensitive_rule_delete():
    pass


@main_api_v2.route('/sensitive_rule_list', methods=['POST'])
def sensitive_rule_list():
    pass


@main_api_v2.route('/sensitive_message_log', methods=['POST'])
def sensitive_message_log():
    pass
