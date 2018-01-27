# -*- coding: utf-8 -*-

from config import db


class UserInfo(db.Model):
    """
    公众号的每一个人的信息
    """
    __tablename__ = 'user_info'
    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 微信给的公众号唯一主键
    open_id = db.Column(db.String(64), index=True, unique=True, nullable=False)  # 28 chars

    # 公众号与小程序的共同主键
    union_id = db.Column(db.String(64), index=True)  # 28 chars

    nick_name = db.Column(db.String(64), index=True, nullable=False)
    sex = db.Column(db.SmallInteger, index=True, nullable=False)
    province = db.Column(db.String(64), index=True, nullable=False)
    city = db.Column(db.String(64), index=True, nullable=False)
    country = db.Column(db.String(64), index=True, nullable=False)
    avatar_url = db.Column(db.String(512))

    # 每次进入公众号时验证用的code
    code = db.Column(db.String(256), index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    last_login_time = db.Column(db.DateTime, index=True, nullable=False)

    token = db.Column(db.String(256), index=True, nullable=False)
    token_expired_time = db.Column(db.DateTime, index=True, nullable=False)

    # 用户的常用设置
    func_send_qun_messages = db.Column(db.Boolean, index=True, nullable=False)
    func_qun_sign = db.Column(db.Boolean, index=True, nullable=False)
    func_auto_reply = db.Column(db.Boolean, index=True, nullable=False)
    func_welcome_message = db.Column(db.Boolean, index=True, nullable=False)


class BotInfo(db.Model):
    """
    机器人的信息
    """
    __tablename__ = 'bot_info'
    wechat_bot_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    wechat_bot_name = db.Column(db.String(128), index=True, nullable=False)


class AccessToken(db.Model):
    """
    存整个公众号的access_token
    """
    __tablename = 'access_token'
    token = db.Column(db.String(128), primary_key=True)
    expired_time = db.Column(db.DateTime)
