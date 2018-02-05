# -*- coding: utf-8 -*-

"""
ws的建立、释放、检测
以及将任务发送给各个安卓
"""
from models.production_consumption_models import ConsumptionTask


def send_task_to_ws(c_task):
    """
    把任务发送给各个安卓端
    :return:
    """

    # 注明类型，开写后可删除
    if isinstance(c_task, ConsumptionTask):
        pass
    # 确定需要发送以后，内容为以下这样

    _send_to_ws(bot_username=c_task.bot_username, target_username=c_task.chatroomname,
                task_send_type=c_task.task_send_type, content=c_task.task_send_content)
    pass


def _send_to_ws(bot_username, target_username, task_send_type, content):
    pass
    # """
    # 将文字发给ws
    # {
    #       "material_id": 1,
    #       "task_send_type": 1,
    #       "task_send_content": {
    #         "text": "这是一段发送的文字。这段文字不能太长，但是预计可以在500字以内"
    #       }
    #     },
    #     {
    #       "material_id": 1,
    #       "task_send_type": 2,
    #       "task_send_content": {
    #         "title": "一个美丽的图片或者什么的",
    #         "description": "一张图片的描述",
    #         "url": "http:"
    #       }
    #     }
    # 发送内容的类型；1为文字；2为公众号；3为链接；4为文件；5为小程序
    # """
    #
    # task_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    # qun_owner_user_id = db.Column(db.BigInteger, index=True, nullable=False)
    # task_initiate_user_id = db.Column(db.BigInteger, index=True, nullable=False)
    # chatroomname = db.Column(db.String(32), index=True, nullable=False)
    #
    # # 1为群发消息；2为自动回复；3为回复签到；4为入群回复
    # task_type = db.Column(db.Integer, index=True, nullable=False)
    #
    # # 发送内容的类型；1为文字；2为公众号；3为链接；4为文件；5为小程序
    # task_send_type = db.Column(db.Integer, index=True, nullable=False)
    # task_send_content = db.Column(db.String(2048), index=True, nullable=False)
    # bot_username = db.Column(db.String(32), index=True, nullable=False)
    #
    # message_received_time = db.Column(db.DateTime, index=True, nullable=False)
    # task_create_time = db.Column(db.DateTime, index=True, nullable=False)
