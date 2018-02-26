# -*- coding: utf-8 -*-

from configs.config import db


class AutoReplySettingInfo(db.Model):
    """
    存储所有的规则
    """
    __tablename__ = "auto_reply_setting_info"
    setting_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    task_covering_qun_count = db.Column(db.Integer, index=True, nullable=False)
    task_covering_people_count = db.Column(db.Integer, index=True, nullable=False)

    is_take_effect = db.Column(db.Boolean, index=True, nullable=False)
    is_deleted = db.Column(db.Boolean, index=True, nullable=False)

    setting_create_time = db.Column(db.DateTime, index=True, nullable=False)


class AutoReplyKeywordRelateInfo(db.Model):
    """
    每个任务的keyword
    """
    __tablename__ = "auto_reply_keyword_relate_Info"
    keyword_rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    setting_id = db.Column(db.BigInteger, index=True, nullable=False)
    keyword = db.Column(db.String(32), index=True, nullable=False)

    # True则必须完全相等
    is_full_match = db.Column(db.Boolean, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)


class AutoReplyMaterialRelate(db.Model):
    """
    每个设置发的物料
    """
    __tablename__ = "auto_reply_material_relate"

    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    setting_id = db.Column(db.BigInteger, index=True, nullable=False)

    material_id = db.Column(db.BigInteger, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)


class AutoReplyTargetRelate(db.Model):
    """
    每个设置发送的群
    """
    __tablename__ = "auto_reply_target_relate"
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    setting_id = db.Column(db.BigInteger, index=True, nullable=False)

    uqun_id = db.Column(db.BigInteger, index=True, nullable=False)

class AutoReplyDefaultSettingInfo(db.Model):
    """
    存储默认的规则模板
    当客户勾选该选项时，需要将该默认规则实例化到用户的设置中
    """
    __tablename__ = "auto_reply_default_setting_info"
    ds_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    create_time = db.Column(db.DateTime, index=True, nullable=False)

class AutoReplyDefaultKeywordRelateInfo(db.Model):
    """
    存储默认的规则模板的关键词
    """
    __tablename__ = "auto_reply_default_keyword_relate_Info"
    keyword_rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    ds_id = db.Column(db.BigInteger, index=True, nullable=False)
    keyword = db.Column(db.String(32), index=True, nullable=False)

    # True则必须完全相等
    is_full_match = db.Column(db.Boolean, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)

class AutoReplyDefaultMaterialRelate(db.Model):
    """
    每个设置发的物料
    """
    __tablename__ = "auto_reply_default_material_relate"

    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ds_id = db.Column(db.BigInteger, index=True, nullable=False)

    dm_id = db.Column(db.BigInteger, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)
