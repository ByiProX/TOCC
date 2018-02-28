# -*- coding: utf-8 -*-

from configs.config import db


class SynchronousAnnouncementDefaultSettingInfo(db.Model):
    """
    存储所有的规则
    """
    __tablename__ = "synchronous_announcement_default_setting_info"
    ds_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    platform_name = db.Column(db.String(16), unique=True, index=True, nullable=False)
    platform_icon = db.Column(db.String(1024))

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


class SynchronousAnnouncementDSUserRelate(db.Model):
    """
    每条规则与用户的联结
    """
    __tablename__ = "synchronous_announcement_ds_user_relate"
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ds_id = db.Column(db.BigInteger, index=True, nullable=False)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)


class BlockCCCrawlNotice(db.Model):
    __tablename__ = "block_cc_crawl_notice"
    aid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    uid = db.Column(db.String(64), index=True, nullable=False)
    lang = db.Column(db.String(16), index=True, nullable=False)
    origin_url = db.Column(db.String(256), index=True, nullable=False)
    created_at = db.Column(db.String(64), index=True, nullable=False)
    zh_name = db.Column(db.String(64), index=True, nullable=False)
    from_source = db.Column(db.String(64), index=True, nullable=False)
    title = db.Column(db.String(512), index=True, nullable=False)
    description = db.Column(db.String(2048), index=True, nullable=False)
    timestamp = db.Column(db.BigInteger, index=True, nullable=False)
    updated_at = db.Column(db.String(64), index=True, nullable=False)
    is_handled = db.Column(db.Boolean, index=True, nullable=False)

    def __init__(self, uid, lang, origin_url, created_at, updated_at, zh_name, from_source, title, description, timestamp):
        self.uid = uid
        self.lang = lang
        self.origin_url = origin_url
        self.created_at = created_at
        self.updated_at = updated_at
        self.zh_name = zh_name
        self.from_source = from_source
        self.description = description
        self.timestamp = timestamp
