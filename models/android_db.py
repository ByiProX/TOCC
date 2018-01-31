# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from config import db

logger = logging.getLogger("main")


class ABot(db.Model):
    __tablename__ = 'a_bot'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    nickname = db.Column(db.String(64), index=True, nullable=False, default="")
    quan_pin = db.Column(db.String(256), index=True, nullable=False, default="")
    py_initial = db.Column(db.String(64), index=True, nullable=False, default="")
    alias = db.Column(db.String(128), index=True, nullable=False, default="")
    chatroom_flag = db.Column(db.Boolean, index=True, nullable=False, default=0)
    verify_flag = db.Column(db.Boolean, index=True, nullable=False, default=0)
    contact_label_ids = db.Column(db.String(256), index=True, nullable=False, default="")
    type = db.Column(db.Integer, index=True, nullable=False)
    show_head = db.Column(db.BigInteger)
    lvbuff = db.Column(db.BLOB)

    imgflag = db.Column(db.Integer)
    img_lastupdatetime = db.Column(db.BigInteger, index=True, nullable=False, default=0)
    avatar_url1 = db.Column(db.String(1024))
    avatar_url2 = db.Column(db.String(1024))
    reserved3 = db.Column(db.Boolean)
    reserved4 = db.Column(db.Integer)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.DateTime, index=True, nullable=False)


class AChatroom(db.Model):
    __tablename__ = 'a_chatroom'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    chatroomname = db.Column(db.String(32), index=True, unique=True, nullable=False)
    addtime = db.Column(db.BigInteger, index=True, nullable=False, default=0)
    memberlist = db.Column(db.Text)
    displayname = db.Column(db.BLOB)
    chatroomnick = db.Column(db.String(64), index=True, nullable=False, default="")
    roomflag = db.Column(db.SmallInteger, index=True, nullable=False, default=0)
    roomowner = db.Column(db.String(32), index=True, nullable=False, default="")
    roomdata = db.Column(db.BLOB)
    is_show_name = db.Column(db.Boolean, index=True, nullable=False, default=1)
    self_display_name = db.Column(db.String(64), index=True, nullable=False, default="")
    style = db.Column(db.Integer, index=True, nullable=False, default=0)
    chatroomdataflag = db.Column(db.Boolean, index=True, nullable=False, default=0)
    modifytime = db.Column(db.BigInteger, index=True, nullable=False)
    chatroomnotice = db.Column(db.Text)
    chatroomnotice_new_version = db.Column(db.Integer)
    chatroomnotice_old_version = db.Column(db.Integer)
    chatroomnotice_editor = db.Column(db.String(32), index=True, nullable=False, default="")
    chatroomnotice_publish_time = db.Column(db.BigInteger, index=True, nullable=False, default=0)
    chatroom_local_version = db.Column(db.BigInteger)
    chatroom_version = db.Column(db.Integer)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.DateTime, index=True, nullable=False)


class AChatroomR(db.Model):
    __tablename__ = 'a_chatroom_r'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    chatroomname = db.Column(db.String(32), index=True, nullable=False)
    username = db.Column(db.String(32), index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.DateTime, index=True, nullable=False)

    db.UniqueConstraint(chatroomname, username, name='ix_a_chatroom_r_name')


class AChatroomOwner(db.Model):
    __tablename__ = 'a_chatroom_owner'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    chatroom_id = db.Column(db.BigInteger, index=True, nullable=True)
    wechat_id = db.Column(db.BigInteger, index=True, nullable=True)
    # 0 -> 存在关系但是不展示; 1 -> 存在旁观关系; 2 -> 存在群主关系
    level = db.Column(db.Integer, index=True, nullable=True, default=0)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    db.UniqueConstraint(chatroom_id, wechat_id, name='ix_a_chatroom_r_name')

    def __init__(self, chatroom_id, wechat_id, level):
        self.chatroom_id = chatroom_id
        self.wechat_id = wechat_id
        self.level = level

    def generate_create_time(self):
        self.create_time = datetime.now()
        return self


class AContact(db.Model):
    __tablename__ = 'a_contact'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    nickname = db.Column(db.String(64), index=True, nullable=False, default="")
    quan_pin = db.Column(db.String(256), index=True, nullable=False, default="")
    py_initial = db.Column(db.String(64), index=True, nullable=False, default="")
    alias = db.Column(db.String(128), index=True, nullable=False, default="")
    chatroom_flag = db.Column(db.Boolean, index=True, nullable=False, default=0)
    verify_flag = db.Column(db.Boolean, index=True, nullable=False, default=0)
    contact_label_ids = db.Column(db.String(256), index=True, nullable=False, default="")
    type = db.Column(db.Integer, index=True, nullable=False)
    show_head = db.Column(db.BigInteger)
    lvbuff = db.Column(db.BLOB)

    imgflag = db.Column(db.Integer)
    img_lastupdatetime = db.Column(db.BigInteger, index=True, nullable=False, default=0)
    avatar_url1 = db.Column(db.String(1024))
    avatar_url2 = db.Column(db.String(1024))
    reserved3 = db.Column(db.Boolean)
    reserved4 = db.Column(db.Integer)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.DateTime, index=True, nullable=False)


class AFriend(db.Model):
    __tablename__ = 'a_friend'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    from_username = db.Column(db.String(32), index=True, nullable=False)
    to_username = db.Column(db.String(32), index=True, nullable=False)
    con_remark = db.Column(db.String(64), index=True, nullable=False, default="")
    con_remark_py_full = db.Column(db.String(256), index=True, nullable=False, default="")
    con_remark_py_short = db.Column(db.String(64), index=True, nullable=False, default="")

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.DateTime, index=True, nullable=False)

    db.UniqueConstraint(from_username, to_username, name='ix_a_friend_name')


class AMember(db.Model):
    __tablename__ = 'a_member'
    chatroomname = db.Column(db.String(32), primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    displayname = db.Column(db.String(64), index=True, nullable=False, default="")

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.DateTime, index=True, nullable=False)
