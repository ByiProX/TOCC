# -*- coding: utf-8 -*-

from configs.config import db


class WelcomeMessageSetting(db.Model):
    """
    用户设置的欢迎语，设置的发送到群的样式等等
    """
    __tablename__ = "welcome_message_setting"
    setting_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    task_covering_qun_count = db.Column(db.Integer, index=True, nullable=False)
    task_covering_people_count = db.Column(db.Integer, index=True, nullable=False)

    is_take_effect = db.Column(db.Boolean, index=True, nullable=False)

    setting_create_time = db.Column(db.DateTime, index=True, nullable=False)


class WelcomeMessageMaterialRelate(db.Model):
    """
    每个设置发的物料
    """
    __tablename__ = "welcome_message_material_relate"

    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    setting_id = db.Column(db.BigInteger, index=True, nullable=False)

    material_id = db.Column(db.BigInteger, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)


class WelcomeMessageTargetRelate(db.Model):
    """
    每个任务设置的词汇
    """
    __tablename__ = "welcome_message_target_relate"

    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    setting_id = db.Column(db.BigInteger, index=True, nullable=False)

    uqun_id = db.Column(db.BigInteger, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)
