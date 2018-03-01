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


first_into_a_qun_and_say_something = """
大家好，我是你们的区块链学习小助手
调用小助手规则：
1.发送#币种名#
助手回复该币种的价格，当前市值，排名，推荐交易所等
2.不定时的推送各大交易所公告，让您掌握第一手消息
3.发送#涨幅榜#
助手回复24小时涨幅前20的名称，涨幅，价格
4.发送#“币种”成交量榜#
助手回复24小时成交量前20的名称，涨幅，24h成交额
5.发送#交易所榜#
助手推送Block.cc的交易量排行榜
6.发送#新币发行#
助手推送Block.cc的新币上线列表
7.发送#行情分析#
助手推送最新公众号文章
8.发送#最新资讯#
助手推送最新公众号文章
9.发送#交易所公告#
助手推送各个网站各个交易所公告"""


def generate_welcome_message_c_task_into_new_qun(uqr_info, user_id, bot_username):
    c_task = ConsumptionTask()

    c_task.qun_owner_user_id = uqr_info.user_id
    c_task.task_initiate_user_id = user_id
    c_task.chatroomname = uqr_info.chatroomname
    c_task.task_type = CONSUMPTION_TASK_TYPE['instruction_when_into_a_qun']
    c_task.task_relevant_id = 0

    c_task.task_send_type = TASK_SEND_TYPE['text']
    c_task.task_send_content = json.dumps({"text": first_into_a_qun_and_say_something})

    c_task.bot_username = bot_username

    c_task.message_received_time = datetime.now()
    c_task.task_create_time = datetime.now()
    db.session.add(c_task)
    db.session.commit()
