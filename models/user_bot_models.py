# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from configs.config import db
from utils.u_model_json_str import model_to_dict


class UserInfo(db.Model):
    """
    公众号的每一个人的信息
    """
    __tablename__ = 'user_info'
    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 微信给的公众号唯一主键
    open_id = db.Column(db.String(64), index=True, unique=True, nullable=False)

    # 公众号与小程序的共同主键
    union_id = db.Column(db.String(64), index=True)

    # 根据nick_name找到的username，可能是错的
    username = db.Column(db.String(64), index=True, nullable=False)

    nick_name = db.Column(db.String(64), index=True, nullable=False)

    # 0为未知 1为男性 2为女性
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

    func_send_qun_messages = db.Column(db.Boolean, index=True, nullable=False)
    func_qun_sign = db.Column(db.Boolean, index=True, nullable=False)
    func_auto_reply = db.Column(db.Boolean, index=True, nullable=False)
    func_welcome_message = db.Column(db.Boolean, index=True, nullable=False)
    func_real_time_quotes = db.Column(db.Boolean, index=True, nullable=False)
    func_synchronous_announcement = db.Column(db.Boolean, index=True, nullable=False)

    def to_dict(self):
        res = model_to_dict(self, self.__class__)
        res.pop('open_id')
        res.pop('union_id')
        res.pop('code')
        res.pop('token_expired_time')
        return res

    @staticmethod
    def get_filter_list(filter_list = None, nickname = None, username = None):
        if filter_list is None:
            filter_list = list()

        if nickname is not None:
            filter_list.append(UserInfo.nick_name == nickname)

        if username is not None:
            filter_list.append(UserInfo.username == username)

        return filter_list


class UserPermission(db.Model):
    """
    记录每个用户每个功能的最高权限
    """
    __tablename__ = 'user_permission'
    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    max_bot_number = db.Column(db.Integer, index=True, nullable=True)
    max_group_number = db.Column(db.Integer, index=True, nullable=True)
    max_qun_number = db.Column(db.Integer, index=True, nullable=True)
    # ！不使用


class UserBotRelateInfo(db.Model):
    """
    用于联结用户和机器人账号，可能是多对多关系
    之后如果有多对多的关系时，每个群里绑定的是哪个机器人是用user_bot_id进行同步
    """
    __tablename__ = 'user_bot_relate_info'
    user_bot_rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    bot_id = db.Column(db.BigInteger, index=True, nullable=False)
    wechat_bot_seq = db.Column(db.Integer, index=True, nullable=True)

    # 用户设置的机器人昵称
    chatbot_default_nickname = db.Column(db.String(32), index=True, nullable=True)

    preset_time = db.Column(db.DateTime, index=True, nullable=False)
    set_time = db.Column(db.DateTime, index=True, nullable=False)
    is_setted = db.Column(db.Boolean, index=True, nullable=False)
    is_being_used = db.Column(db.Boolean, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)

    db.UniqueConstraint(user_id, bot_id, name='ix_user_bot_relate_user_id_wechat_two_id')

    def to_dict(self):
        res = model_to_dict(self, self.__class__)
        return res


class BotInfo(db.Model):
    """
    bot的状态以及和真实bot的联查
    """
    bot_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    # 安卓端返回的唯一id
    username = db.Column(db.String(32), index=True, unique=True, nullable=True)

    create_bot_time = db.Column(db.DateTime, index=True, nullable=False)
    is_alive = db.Column(db.Boolean, index=True, nullable=False)
    alive_detect_time = db.Column(db.DateTime, index=True, nullable=False)
    qr_code = db.Column(db.String(256), nullable=True)

    def to_dict(self):
        res = model_to_dict(self, self.__class__)
        res.pop('username')
        return res


class AccessToken(db.Model):
    """
    存整个公众号的access_token
    """
    __tablename = 'access_token'
    token = db.Column(db.String(191), primary_key=True)  # 256
    expired_time = db.Column(db.DateTime)

    def load_from_json(self, access_token_json):
        self.token = access_token_json.get('access_token')
        expires_in = access_token_json.get('expires_in')
        self.expired_time = datetime.now() + timedelta(seconds=expires_in)
        return self
