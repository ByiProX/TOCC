# -*- coding: utf-8 -*-

from config import db


class UserSignSetting(db.Model):
    """
    用户设置的群签到设置
    """
    pass


class SignStream(db.Model):
    """
    群签到的签到流
    """
    pass


class UserContinueSignStatistics(db.Model):
    """
    用户持续签到情况
    """
    pass


class UserSignPointsStatistics(db.Model):
    """
    用户的积分情况
    """
    pass
