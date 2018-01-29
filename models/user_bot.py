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

    # 0为女性 1为男性
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


class UserBotRelateInfo(db.Model):
    """
    用于联结用户和机器人账号，可能是多对多关系
    之后如果有多对多的关系时，每个群里绑定的是哪个机器人是用user_bot_id进行同步
    """
    __tablename__ = 'user_bot_relate_info'
    user_bot_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    wechat_bot_id = db.Column(db.BigInteger, index=True, nullable=False)
    wechat_bot_seq = db.Column(db.Integer, index=True, nullable=False)

    db.UniqueConstraint(user_id, wechat_bot_id, name='ix_user_bot_relate_user_id_wechat_two_id')


class WechatBotInfo(db.Model):
    """
    机器人的信息
    """
    # 这里可能有一个状态问题，就是bot的资源用光了
    __tablename__ = 'wechat_bot_info'
    wechat_bot_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    wechat_bot_name = db.Column(db.String(128), index=True, nullable=False)


class AccessToken(db.Model):
    """
    存整个公众号的access_token
    """
    __tablename = 'access_token'
    token = db.Column(db.String(128), primary_key=True)
    expired_time = db.Column(db.DateTime)
