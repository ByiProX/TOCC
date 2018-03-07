# -*- coding: utf-8 -*-

from configs.config import db


class CoinWalletQunMemberRelate(db.Model):
    """
    将有地址的人的信息存在这里
    """
    __tablename__ = "coin_wallet_qun_member_relate"
    uqun_member_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 冗余，做查询方便用
    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    # 唯一关系绑定
    uqun_id = db.Column(db.BigInteger, index=True, nullable=False)
    member_username = db.Column(db.String(32), index=True, nullable=True)

    member_is_deleted = db.Column(db.Boolean, index=True, nullable=False)
    last_update_time = db.Column(db.DateTime, index=True, nullable=False)

    db.UniqueConstraint(uqun_id, member_username, name='ix_coin_wallet_qun_member_relate_rid')


class CoinWalletMemberAddressRelate(db.Model):
    """
    将钱包地址绑在每个人身上
    """
    __tablename__ = "coin_wallet_member_address_relate"
    wallet_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    uqun_member_id = db.Column(db.BigInteger, index=True, nullable=False)

    coin_address = db.Column(db.String(256), index=True, nullable=False)

    address_is_origin = db.Column(db.Boolean, index=True, nullable=False)

    wallet_is_deleted = db.Column(db.Boolean, index=True, nullable=False)

    found_in_qun_time = db.Column(db.DateTime, index=True, nullable=False)
    last_updated_time = db.Column(db.DateTime, index=True, nullable=False)
