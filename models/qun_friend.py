# -*- coding: utf-8 -*-

from config import db
from models.android_db import AChatroom



class QunInfo(db.Model):
    """
    每个人的群信息
    """
    __tablename__ = "qun_info"
    qun_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    qun_name = db.Column(db.String(16), index=True, nullable=False)
    a_chatroomname = db.Column(db.String(32), index=True, nullable=False)
    is_admin = 1


    db.UniqueConstraint(user_id, a_chatroomname, name = 'ix_qun_info_a_chatroomname_user_id')


class GroupInfo(db.Model):
    """
    存储用户的分组

    """
    __tablename__ = "group_info"
    group_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 组名称，如果不设置则有默认
    group_name = db.Column(db.String(16), index=True,nullable=False)

    user_id = db.Column(db.BigInteger, index=True,nullable=False)
    group_seq = db.Column(db.Integer,index=True,nullable=False)

class MemberInfo(db.Model):
    """
    群内好友
    """
    __tablename__ = "member_info"
    member_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    qun_id = 1




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
