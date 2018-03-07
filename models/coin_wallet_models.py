# -*- coding: utf-8 -*-

from configs.config import db


class CoinWalletInfo(db.Model):
    """
    钱包地址的基本信息及管理均在此表中
    """
    __tablename__ = "coin_wallet_info"
    wallet_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 实际主键
    uqun_id = db.Column(db.BigInteger, index=True, nullable=False)
    member_username = db.Column(db.String(32), index=True, nullable=True)

    # 冗余，做查询方便用
    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    coin_address = db.Column(db.String(256), index=True, nullable=False)

    address_is_origin = db.Column(db.Boolean, index=True, nullable=False)

    wallet_is_deleted = db.Column(db.Boolean, index=True, nullable=False)

    found_in_qun_time = db.Column(db.DateTime, index=True, nullable=False)
    last_updated_time = db.Column(db.DateTime, index=True, nullable=False)
