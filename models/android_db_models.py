# -*- coding: utf-8 -*-
import logging
from time import sleep

from configs.config import db

logger = logging.getLogger("main")


class ABot(db.Model):
    __tablename__ = 'a_bot'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    # nickname = db.Column(db.String(64), index=True, nullable=False, default="")
    # quan_pin = db.Column(db.String(256), index=True, nullable=False, default="")
    # py_initial = db.Column(db.String(64), index=True, nullable=False, default="")
    nickname = db.Column(db.BLOB)
    quan_pin = db.Column(db.BLOB)
    py_initial = db.Column(db.BLOB)
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
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)


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
    chatroomnotice = db.Column(db.BLOB)
    chatroomnotice_new_version = db.Column(db.Integer)
    chatroomnotice_old_version = db.Column(db.Integer)
    chatroomnotice_editor = db.Column(db.String(32), index=True, nullable=False, default="")
    chatroomnotice_publish_time = db.Column(db.BigInteger, index=True, nullable=False, default=0)
    chatroom_local_version = db.Column(db.BigInteger)
    chatroom_version = db.Column(db.Integer)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)


class AChatroomR(db.Model):
    __tablename__ = 'a_chatroom_r'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    chatroomname = db.Column(db.String(32), index=True, nullable=False)
    username = db.Column(db.String(32), index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    db.UniqueConstraint(chatroomname, username, name='ix_a_chatroom_r_name')

    @staticmethod
    def get_a_chatroom_r(chatroomname, username):
        a_chatroom_r = None
        times = 3
        while times:
            a_chatroom_r = db.session.query(AChatroomR).filter(AChatroomR.username == username,
                                                               AChatroomR.chatroomname == chatroomname).first()
            if a_chatroom_r:
                break
            sleep(1)
            times -= 1

        return a_chatroom_r


class AContact(db.Model):
    __tablename__ = 'a_contact'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True, unique=True, nullable=False)
    nickname = db.Column(db.BLOB)
    quan_pin = db.Column(db.BLOB)
    py_initial = db.Column(db.BLOB)
    # nickname = db.Column(db.String(64), index=True, nullable=False, default="")
    # quan_pin = db.Column(db.String(256), index=True, nullable=False, default="")
    # py_initial = db.Column(db.String(64), index=True, nullable=False, default="")
    alias = db.Column(db.String(128), index=True, nullable=False, default="")
    chatroom_flag = db.Column(db.Boolean, index=True, nullable=False, default=0)
    verify_flag = db.Column(db.Boolean, index=True, nullable=False, default=0)
    contact_label_ids = db.Column(db.String(256), index=True, nullable=False, default="")
    show_head = db.Column(db.BigInteger)
    lvbuff = db.Column(db.BLOB)

    imgflag = db.Column(db.Integer)
    img_lastupdatetime = db.Column(db.BigInteger, index=True, nullable=False, default=0)
    avatar_url1 = db.Column(db.String(1024))
    avatar_url2 = db.Column(db.String(1024))
    reserved3 = db.Column(db.Boolean)
    reserved4 = db.Column(db.Integer)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    member_count = db.Column(db.Integer, index=True, nullable=False)

    @staticmethod
    def get_a_contact(username):
        a_contact = None
        times = 3
        while times:
            a_contact = db.session.query(AContact).filter(AContact.username == username).first()
            if a_contact:
                break
            sleep(1)
            times -= 1

        return a_contact


class AFriend(db.Model):
    __tablename__ = 'a_friend'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    from_username = db.Column(db.String(32), index=True, nullable=False)
    to_username = db.Column(db.String(32), index=True, nullable=False)
    con_remark = db.Column(db.String(64), index=True, nullable=False, default="")
    con_remark_py_full = db.Column(db.String(256), index=True, nullable=False, default="")
    con_remark_py_short = db.Column(db.String(64), index=True, nullable=False, default="")
    type = db.Column(db.Integer, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    db.UniqueConstraint(from_username, to_username, name='ix_a_friend_name')

    @staticmethod
    def get_a_friend(from_username, to_username):
        a_friend = None
        times = 3
        while times:
            a_friend = db.session.query(AFriend).filter(AFriend.from_username == from_username,
                                                        AFriend.to_username == to_username).first()
            if a_friend:
                break
            sleep(1)
            times -= 1

        return a_friend


class AMember(db.Model):
    __tablename__ = 'a_member'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    chatroomname = db.Column(db.String(32), index=True, nullable=True)
    username = db.Column(db.String(32), index=True, nullable=False)
    displayname = db.Column(db.String(64), index=True, nullable=False, default="")
    is_deleted = db.Column(db.Boolean, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    db.UniqueConstraint(chatroomname, username, name='ix_a_member_name')

    @staticmethod
    def get_filter_list(filter_list = None, chatroomname = None, username = None, displayname = None, is_deleted = None):
        if filter_list is None:
            filter_list = list()

        if chatroomname is not None:
            filter_list.append(AMember.chatroomname == chatroomname)

        if username is not None:
            filter_list.append(AMember.username == username)

        if displayname is not None:
            filter_list.append(AMember.displayname == displayname)

        if is_deleted is not None:
            filter_list.append(AMember.is_deleted == is_deleted)

        return filter_list


class AMessage(db.Model):
    __tablename__ = 'a_message'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    msg_local_id = db.Column(db.String(64), index=True, nullable=False)
    username = db.Column(db.String(32), index=True, nullable=False)

    msg_svr_id = db.Column(db.String(64), index=True, nullable=False)
    type = db.Column(db.Integer, index=True, nullable=False)
    status = db.Column(db.Integer, index=True, nullable=False)
    is_send = db.Column(db.Boolean, index=True, nullable=False)
    talker = db.Column(db.String(32), index=True, nullable=False)
    content = db.Column(db.BLOB)
    img_path = db.Column(db.String(256))
    reserved = db.Column(db.BLOB)

    create_time = db.Column(db.DateTime, index=True, nullable=False)

    db.UniqueConstraint(msg_local_id, username, name='ix_a_message_id')


class ABotPingLog(db.Model):
    __tablename__ = 'a_bot_ping_log'

    aid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.TIMESTAMP, nullable=False)
    bot_username = db.Column(db.String(32), index=True, nullable=False)
    status = db.Column(db.Boolean, index=True, nullable=False)
