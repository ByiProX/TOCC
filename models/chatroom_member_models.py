# -*- coding: utf-8 -*-
import logging

from configs.config import db

logger = logging.getLogger("main")


class ChatroomInfo(db.Model):
    """
    一个 Chatroom 只维护一份 info 和 statistic
    chatroom_id: AChatroom.id
    """
    __tablename__ = "chatroom_info"
    chatroom_id = db.Column(db.BigInteger, primary_key=True)
    chatroomname = db.Column(db.String(32), index=True, unique=True, nullable=False)

    bz_value = db.Column(db.DECIMAL(5, 2), index=True)
    # participative_count = db.Column(db.Integer, index = True)
    # interactive_index = db.Column(db.Float, index = True)
    # participative_index = db.Column(db.Float, index = True)
    # health_index = db.Column(db.Float, index = True)

    # active_count 更新 flag

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)


class BotChatroomR(db.Model):
    """
    a_chatroom_r_id: AChatroomR.id
    """
    __tablename__ = 'bot_chatroom_r'
    a_chatroom_r_id = db.Column(db.BigInteger, primary_key=True)
    chatroomname = db.Column(db.String(32), index=True, nullable=False)
    username = db.Column(db.String(32), index=True, nullable=False)

    is_on = db.Column(db.Boolean, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    db.UniqueConstraint(chatroomname, username, name='ix_bot_chatroom_r_name')


class UserChatroomR(db.Model):
    __tablename__ = "user_chatroom_r"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    chatroom_id = db.Column(db.BigInteger, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)

    db.UniqueConstraint(user_id, chatroom_id, name='ix_user_chatroom_r_id')


class MemberInfo(db.Model):
    """
    member_id: AMember.id
    """
    __tablename__ = "member_info"
    member_id = db.Column(db.BigInteger, primary_key=True)
    chatroomname = db.Column(db.String(32), index=True, nullable=True)
    username = db.Column(db.String(32), index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    db.UniqueConstraint(chatroomname, username, name='ix_a_member_name')


class ChatroomOverview(db.Model):
    __tablename__ = "chatroom_overview"
    chatroom_id = db.Column(db.BigInteger, primary_key=True)
    scope = db.Column(db.Integer, primary_key=True)

    speak_count = db.Column(db.BigInteger, index=True)
    incre_count = db.Column(db.BigInteger, index = True)
    active_count = db.Column(db.BigInteger, index = True)
    active_rate = db.Column(db.DECIMAL(5, 2), index = True)

    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)


class ChatroomStatistic(db.Model):
    __tablename__ = "chatroom_statistic"


class MemberOverview(db.Model):
    __tablename__ = "member_overview"


class MemberStatistic(db.Model):
    __tablename__ = "member_statistic"
