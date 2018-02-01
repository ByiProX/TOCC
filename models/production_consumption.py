# -*- coding: utf-8 -*-
from configs.config import db


class TaskGenerationRule(db.Model):
    """
    存放每个人在每个群设置的规则
    """


class ConsumptionTask(db.Model):
    """
    存放由production生成的任务
    """
    __tablename__ = 'consumption_task'
    task_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    qun_owner_user_id = db.Column(db.BigInteger, index=True, nullable=False)
    task_initiate_user_id = db.Column(db.BigInteger, index=True, nullable=False)
    chatroomname = db.Column(db.String(32), index=True, nullable=False)

    # 1为群发消息；2为自动回复；3为回复签到；4为入群回复
    task_type = db.Column(db.Integer, index=True, nullable=False)

    # 发送内容的类型，
    task_send_type = db.Column(db.Integer, index=True, nullable=False)
    task_send_content = db.Column(db.String(2048), index=True, nullable=False)
    bot_username = db.Column(db.String(32), index=True, nullable=False)

    message_received_time = db.Column(db.DateTime, index=True, nullable=False)
    task_create_time = db.Column(db.DateTime, index=True, nullable=False)


class ProductionStatistic(db.Model):
    """
    每次扫描的情况记录在这里
    """
    __tablename__ = 'production_statistic'
    sid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    last_a_message_id = db.Column(db.BigInteger, index=True, nullable=False)
    last_a_message_create_time = db.Column(db.DateTime, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
