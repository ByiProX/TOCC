# -*- coding: utf-8 -*-

from configs.config import db


class allcoinsdefaultsettinginfo(db.Model):
    """
    存储所有的规则
    """
    __tablename__ = "all_coins_default_setting_info"
    ds_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    #优先级顺序
    priority = db.Column(db.String(16),unique=True, index=True, nullable=False)
    # 简称
    symbol = db.Column(db.String(16), unique=True, index=True, nullable=False)
    # 全称
    coin_name = db.Column(db.String(64), index=True, nullable=False)
    # 图标
    coin_icon = db.Column(db.String(1024))
    # 24 小时涨幅
    change1d = db.Column(db.DECIMAL(10, 2), index=True, nullable=False)
    change1h = db.Column(db.DECIMAL(10, 2), index=True, nullable=False)
    change7d = db.Column(db.DECIMAL(10, 2), index=True, nullable=False)
    # 当前市值
    marketcap = db.Column(db.DECIMAL(30, 15), index=True, nullable=False)
    # 当前币数量
    available_supply = db.Column(db.DECIMAL(30, 15), index=True, nullable=False)
    # 当前交易价
    price = db.Column(db.DECIMAL(30, 15), index=True, nullable=False)
    # 交易量
    volume_ex = db.Column(db.DECIMAL(30, 15), index=True, nullable=False)
    #是否可开采
    mineable = db.Column(db.String(2),unique=True, index=True, nullable=False)

    def __init__(self, priority, symbol, coin_name, coin_icon, change1d, change1h,change7d, marketcap, available_supply, price,
                 volume_ex, mineable):
        self.priority = priority
        self.symbol = symbol
        self.coin_name = coin_name
        #没有中文名
        #self.coin_name_cn = coin_name_cn
        self.coin_icon = coin_icon
        self.available_supply = available_supply
        self.change1d = change1d
        self.change7d = change7d
        self.change1h = change1h
        self.price = price
        self.volume_ex = volume_ex
        self.marketcap = marketcap
        self.mineable = mineable
