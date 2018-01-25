# -*- coding: utf-8 -*-

from config import db
from utils.u_model_json_str import model_to_dict


class UserInfo(db.Model):
    """
    公众号的每一个人的信息
    """
    __tablename__ = 'wechat'
    user_id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)

    open_id = db.Column(db.String(64), index = True)  # 28 chars
    union_id = db.Column(db.String(64), index = True)  # 28 chars
    nick_name = db.Column(db.String(64), index = True)
    avatar_url = db.Column(db.String(512))
    sex = db.Column(db.Integer, index = True)
    province = db.Column(db.String(64), index = True)
    city = db.Column(db.String(64), index = True)
    country = db.Column(db.String(64), index = True)
    code = db.Column(db.String(256), index = True)
    create_time = db.Column(db.DateTime, index = True)
    last_login_time = db.Column(db.DateTime, index = True)

    def to_json(self):
        res = model_to_dict(self, self.__class__)
        res['wechat_id'] = self.id
        res.pop('user_id')
        res.pop('open_id')
        res.pop('union_id')
        res.pop('uin')
        res.pop('sms_code')
        res.pop('sms_code_expired_time')
        res.pop('sale_id')
        res.pop('is_test')
        res.pop('contact_id')
        res.pop('expired_time')
        res.pop('token')
        res.pop('code')
        return res


class BotInfo(db.Model):
    """
    机器人的信息（手机、板子）
    """
    __tablename__ = 'bot'
    wechat_bot_id = db.Column(db.BigInteger, primary_key = True, autoincrement = True)



class AccessToken(db.Model):
    __tablename = 'access_token'
    token = db.Column(db.String(128), primary_key=True)
    expired_time = db.Column(db.DateTime)
