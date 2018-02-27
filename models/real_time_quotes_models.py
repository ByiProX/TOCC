# -*- coding: utf-8 -*-

from configs.config import db


class RealTimeQuotesDefaultSettingInfo(db.Model):
    """
    存储所有的规则
    """
    __tablename__ = "real_time_quotes_default_setting_info"
    ds_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    create_time = db.Column(db.DateTime, index=True, nullable=False)


class RealTimeQuotesDefaultKeywordRelateInfo(db.Model):
    """
    存储默认的规则模板的关键词
    """
    __tablename__ = "real_time_quotes_default_keyword_relate_Info"
    keyword_rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    ds_id = db.Column(db.BigInteger, index=True, nullable=False)
    keyword = db.Column(db.String(32), index=True, nullable=False)

    # True则必须完全相等
    is_full_match = db.Column(db.Boolean, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)


class RealTimeQuotesDefaultMaterialRelate(db.Model):
    """
    每个设置发的物料
    """
    __tablename__ = "real_time_quotes_default_material_relate"

    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ds_id = db.Column(db.BigInteger, index=True, nullable=False)

    dm_id = db.Column(db.BigInteger, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)


class RealTimeQuotesDSUQBRelate(db.Model):
    """
    每条规则与群的联结
    """
    __tablename__ = "real_time_quotes_ds_uqb_relate"
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ds_id = db.Column(db.BigInteger, index=True, nullable=False)
    uqb_rid = db.Column(db.BigInteger, index=True, nullable=False)
