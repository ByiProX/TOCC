# -*- coding: utf-8 -*-

from config import db

class UserFriend(db.Model):
    """
    需要用到的用户的好友
    """
    pass

class UserQun(db.Model):
    """
    每个人的群信息
    """
    pass


class UserQunGroupInfo(db.Model):
    """
    每个人的群的分类信息
    """
    pass
