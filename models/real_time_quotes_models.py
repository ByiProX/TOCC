# -*- coding: utf-8 -*-

from configs.config import db


class RealTimeQuotesDefaultSettingInfo(db.Model):
    """
    存储所有的规则
    """
    __tablename__ = "real_time_quotes_default_setting_info"
    ds_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    # 简称
    symbol = db.Column(db.String(16), unique = True, index = True, nullable = False)
    # 全称
    coin_name = db.Column(db.String(16), unique = True, index = True, nullable = False)
    # 中文名
    coin_name_cn = db.Column(db.String(32), index = True, nullable = False)
    coin_icon = db.Column(db.String(1024))
    # 排名
    rank = db.Column(db.Integer, index = True, nullable = False)
    # 24 小时涨幅
    change1d = db.Column(db.DECIMAL(1, 3), index = True, nullable = False)

    change1h = db.Column(db.DECIMAL(1, 3), index = True, nullable = False)
    change7d = db.Column(db.DECIMAL(1, 3), index = True, nullable = False)
    # 当前市值
    marketcap = db.Column(db.DECIMAL(20, 20), index = True, nullable = False)
    # 当前币数量
    available_supply = db.Column(db.DECIMAL(20, 20), index = True, nullable = False)
    # 当前交易价
    price = db.Column(db.DECIMAL(20, 20), index = True, nullable = False)
    # 交易量
    volume_ex = db.Column(db.DECIMAL(20, 20), index = True, nullable = False)

    # 推荐交易所
    suggest_ex1 = db.Column(db.String(64), index = True, nullable = False)
    suggest_ex2 = db.Column(db.String(64), index = True, nullable = False)
    suggest_ex1_url = db.Column(db.String(1024))
    suggest_ex2_url = db.Column(db.String(1024))

    # deprecated
    # 前推 24 小时交易价
    open = db.Column(db.DECIMAL(20, 20), index = True, nullable = False)
    # 当前交易价
    close = db.Column(db.DECIMAL(20, 20), index = True, nullable = False)
    # 24 小时成交额
    vol = db.Column(db.DECIMAL(20, 20), index = True, nullable = False)

    # 数据完整性
    is_integral = db.Column(db.Boolean, index = True, nullable = False)

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


class RealTimeQuotesDSUserRelate(db.Model):
    """
    每条规则与用户的联结
    """
    __tablename__ = "real_time_quotes_ds_user_relate"
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ds_id = db.Column(db.BigInteger, index=True, nullable=False)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)