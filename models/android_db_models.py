# -*- coding: utf-8 -*-
import logging
from time import sleep

from configs.config import db, MSG_TYPE_SYS, MSG_TYPE_TXT
from models.message_ext_models import MessageAnalysis
from utils.u_transformat import str_to_unicode

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

    @staticmethod
    def analysis_and_save_a_message(a_message):
        """
        用于将a_message信息放入库中，并返回库中的结构模样
        :param a_message:
        :return:
        """
        if not isinstance(a_message, AMessage):
            # Mark
            # 几乎不报错，报错需要查错
            raise TypeError(u'AMessage Type Err')
        msg_ext = MessageAnalysis(a_message)
        content = str_to_unicode(msg_ext.content)
        is_send = msg_ext.is_send
        talker = msg_ext.talker
        msg_type = msg_ext.type

        # is_to_friend
        if msg_ext.talker.find(u'@chatroom') != -1:
            is_to_friend = False
        else:
            is_to_friend = True
        msg_ext.is_to_friend = is_to_friend

        # real_talker & real_content
        if is_to_friend or is_send or msg_type == MSG_TYPE_SYS:
            real_talker = talker
            real_content = content
        elif msg_type != MSG_TYPE_TXT:
            # 除了 TXT 和 SYS 的处理
            real_content = content
            if content.find(u':') == -1:
                # Mark: 收到的群消息没有 ':\n'，需要查错
                logger.info(u"ERR: chatroom msg received doesn't have ':', msg_id: " + unicode(
                    msg_ext.msg_id) + u" type: " + unicode(msg_type))
                raise ValueError(u"ERR: chatroom msg received doesn't have ':', msg_id: " + unicode(
                    msg_ext.msg_id) + u" type: " + unicode(msg_type))
            content_part = content.split(u':')
            real_talker = content_part[0]
        else:
            if content.find(u':\n') == -1:
                # Mark: 收到的群消息没有 ':\n'，需要查错
                logger.info(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(
                    msg_ext.msg_id) + u" type: " + unicode(msg_type))
                raise ValueError(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(
                    msg_ext.msg_id) + u" type: " + unicode(msg_type))
            content_part = content.split(u':\n')
            real_talker = content_part[0]
            real_content = content_part[1]

        msg_ext.real_talker = real_talker
        msg_ext.real_content = unicode_to_str(real_content)

        return msg_ext


class ABotPingLog(db.Model):
    __tablename__ = 'a_bot_ping_log'

    aid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.TIMESTAMP, nullable=False)
    bot_username = db.Column(db.String(32), index=True, nullable=False)
    status = db.Column(db.Boolean, index=True, nullable=False)
