# -*- coding: utf-8 -*-

"""
ws的建立、释放、检测
以及将任务发送给各个安卓
"""
from models.production_consumption import ConsumptionTask


def send_task_to_ws(c_task):
    """
    把任务发送给各个安卓端
    :return:
    """

    # 注明类型，开写后可删除
    if isinstance(c_task, ConsumptionTask):
        pass
    pass


def _send_to_ws(bot_username, target_username, content):
    """
    将文字发给ws
    :param bot_username:
    :param target_username:
    :param content:
    :return:
    """
