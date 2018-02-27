# -*- coding: utf-8 -*-

from configs.config import db


class SynchronousAnnouncementDefaultSettingInfo(db.Model):
    """
    存储所有的规则
    """
    __tablename__ = "synchronous_announcement_default_setting_info"
    ds_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    create_time = db.Column(db.DateTime, index=True, nullable=False)


class SynchronousAnnouncementDefaultKeywordRelateInfo(db.Model):
    """
    存储默认的规则模板的关键词
    """
    __tablename__ = "synchronous_announcement_default_keyword_relate_Info"
    keyword_rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    ds_id = db.Column(db.BigInteger, index=True, nullable=False)
    keyword = db.Column(db.String(32), index=True, nullable=False)

    # True则必须完全相等
    is_full_match = db.Column(db.Boolean, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)


class SynchronousAnnouncementDefaultMaterialRelate(db.Model):
    """
    每个设置发的物料
    """
    __tablename__ = "synchronous_announcement_default_material_relate"

    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ds_id = db.Column(db.BigInteger, index=True, nullable=False)

    dm_id = db.Column(db.BigInteger, index=True, nullable=False)
    send_seq = db.Column(db.Integer, index=True, nullable=False)


class SynchronousAnnouncementDSUQBRelate(db.Model):
    """
    每条规则与群的联结
    """
    __tablename__ = "synchronous_announcement_ds_uqb_relate"
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ds_id = db.Column(db.BigInteger, index=True, nullable=False)
    uqb_rid = db.Column(db.BigInteger, index=True, nullable=False)


class BlockCCCrawlData(db.Model):
    __tablename__ = "block_cc_crawl_data"
    aid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(64), index=True, nullable=False)
    lang = db.Column(db.String(16), index=True, nullable=False)
    originUrl = db.Column(db.String(256), index=True, nullable=False)
    createdAt = db.Column(db.String(64), index=True, nullable=False)
    zh_name = db.Column(db.String(64), index=True, nullable=False)
    from_source = db.Column(db.String(64), index=True, nullable=False)
    title = db.Column(db.String(256), index=True, nullable=False)
    description = db.Column(db.String(2048), index=True, nullable=False)
    timestamp = db.Column(db.BigInteger, index=True, nullable=False)
    updatedAt = db.Column(db.String(64), index=True, nullable=False)
