# -*- coding: utf-8 -*-

from config import db


class UserQunInfo(db.Model):
    """
    每个人的群信息
    """
    pass
    qun_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True)


class UserQunFriendInfo(db.Model):
    """
    每个用户的群的好友的信息
    """
    pass
    friend_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True)
    qun_id = db.Column(db.BigInteger, index=True)


class UserQunGroupInfo(db.Model):
    """
    每个人的群的分类信息
    """
    pass
    qun_group_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True)
    qun_id = db.Column(db.BigInteger, index=True)
