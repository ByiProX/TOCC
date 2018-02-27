# -*- coding: utf-8 -*-
import json
import logging

from datetime import datetime

from configs.config import CONSUMPTION_TASK_TYPE, TASK_SEND_TYPE, db
from models.production_consumption_models import ConsumptionTask

logger = logging.getLogger('main')


def check_whether_message_is_friend_into_qun(message_analysis):
    """
    根据一条message
    :param message_analysis:
    :return:
    """


def _is_friend_into_qun():
    """

    :return:
    """


def generate_welcome_message_c_task_into_new_qun(uqr_info, user_id, bot_username):
    c_task = ConsumptionTask()

    c_task.qun_owner_user_id = uqr_info.user_id
    c_task.task_initiate_user_id = user_id
    c_task.chatroomname = uqr_info.chatroomname
    c_task.task_type = CONSUMPTION_TASK_TYPE['instruction_when_into_a_qun']
    c_task.task_relevant_id = 0

    c_task.task_send_type = TASK_SEND_TYPE['text']
    c_task.task_send_content = json.dumps({"text": "欢迎大家使用友问币答！~"})

    c_task.bot_username = bot_username

    c_task.message_received_time = datetime.now()
    c_task.task_create_time = datetime.now()
    db.session.add(c_task)
    db.session.commit()
