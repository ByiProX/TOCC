# -*- coding: utf-8 -*-

from config import db


class OrganizationInfo(db.Model):
    """
    记录一个公司或组织的信息
    """
    __tablename__ = 'organization_info'
    organization_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    organization_name = db.Column(db.String(32), index=True, nullable=False)


class OrganizationUserRelate(db.Model):
    """
    用于标记一个组织中有哪些用户
    """
    __tablename__ = 'organization_user_relate'
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    organization_id = db.Column(db.BigInteger, index=True, nullable=False)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    is_org_admin = db.Column(db.Boolean, index=True, nullable=False)

    db.UniqueConstraint(organization_id, user_id, name='ix_organization_user_relate_two_id')


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

    # 用户的常用设置
    func_send_qun_messages = db.Column(db.Boolean, index=True, nullable=False)
    func_qun_sign = db.Column(db.Boolean, index=True, nullable=False)
    func_auto_reply = db.Column(db.Boolean, index=True, nullable=False)
    func_welcome_message = db.Column(db.Boolean, index=True, nullable=False)


class UserBotRelate(db.Model):
    """
    用于联结用户和机器人账号，可能是多对多关系
    """
    __tablename__ = 'user_bot_relate'
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    wechat_bot_id = db.Column(db.BigInteger, index=True, nullable=False)

    db.UniqueConstraint(user_id, wechat_bot_id, name='ix_user_bot_relate_user_id_wechat_two_id')


class WechatBotInfo(db.Model):
    """
    机器人的信息
    """
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
