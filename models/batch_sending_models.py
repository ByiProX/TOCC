# -*- coding: utf-8 -*-

from configs.config import db


class BatchSendingTaskInfo(db.Model):
    """
    用户提出的群发消息的任务
    """
    __tablename__ = "batch_sending_task_info"
    sending_task_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    task_covering_qun_count = db.Column(db.Integer, index=True, nullable=False)
    task_covering_people_count = db.Column(db.Integer, index=True, nullable=False)

    # 显示的任务状态；状态码未确定
    task_status = db.Column(db.Integer, index=True, nullable=False)
    task_status_content = db.Column(db.String(2048), index=True, nullable=False)

    task_create_time = db.Column(db.DateTime, index=True, nullable=False)


class BatchSendingTaskMaterialRelate(db.Model):
    """
    用户的每个物料记录
    """
    __tablename__ = "batch_sending_task_material_relate"
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sending_task_id = db.Column(db.BigInteger, index=True, nullable=False)

    material_id = db.Column(db.BigInteger, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)


class BatchSendingTaskTargetRelate(db.Model):
    """
    每个任务
    """
    __tablename__ = "batch_sending_task_target_relate"
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sending_task_id = db.Column(db.BigInteger, index=True, nullable=False)

    uqun_id = db.Column(db.BigInteger, index=True, nullable=False)
