# -*- coding: utf-8 -*-

from config import db
from utils.u_model_json_str import model_to_dict


class Wechat(db.Model):
    """
    公众号的每一个人的信息
    """
    __tablename__ = 'wechat'

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


class Bot(db.Model):
    """
    机器人的信息（手机、板子）
    """
    __tablename__ = 'bot'


class AccessToken(db.Model):
    __tablename = 'access_token'
    token = db.Column(db.String(128), primary_key=True)
    expired_time = db.Column(db.DateTime)
