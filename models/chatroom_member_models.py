# -*- coding: utf-8 -*-
import logging
from decimal import Decimal

from datetime import datetime

from configs.config import db, MAX_MEMBER_COUNT_DECIMAL

logger = logging.getLogger("main")


class ChatroomInfo(db.Model):
    """
    一个 Chatroom 只维护一份 info 和 statistic
    chatroom_id: AContact.id
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

    def __init__(self, chatroom_id, chatroomname, member_count):
        self.chatroom_id = chatroom_id
        self.chatroomname = chatroomname

        self.bz_value = Decimal(member_count) / MAX_MEMBER_COUNT_DECIMAL

    def generate_create_time(self, create_time = None):
        if create_time is None:
            create_time = datetime.now()
        self.create_time = create_time
        return self


class BotChatroomR(db.Model):
    """
    bot 对群的管理开关状态
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

    def __init__(self, a_chatroom_r_id, chatroomname, username, is_on = False):
        self.a_chatroom_r_id = a_chatroom_r_id
        self.chatroomname = chatroomname
        self.username = username
        self.is_on = is_on

    def generate_create_time(self, create_time = None):
        if create_time is None:
            create_time = datetime.now()
        self.create_time = create_time
        return self


class UserChatroomR(db.Model):
    __tablename__ = "user_chatroom_r"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    chatroom_id = db.Column(db.BigInteger, index=True, nullable=False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)

    db.UniqueConstraint(user_id, chatroom_id, name='ix_user_chatroom_r_id')

    def __init__(self, user_id, chatroom_id):
        self.user_id = user_id
        self.chatroom_id = chatroom_id

    def generate_create_time(self, create_time = None):
        if create_time is None:
            create_time = datetime.now()
        self.create_time = create_time
        return self


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


class ChatroomActive(db.Model):
    __tablename__ = "chatroom_active"
    chatroom_id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(32), primary_key=True)
    time_to_day = db.Column(db.DateTime, primary_key=True)

    create_time = db.Column(db.DateTime, index=True)


class ChatroomStatistic(db.Model):
    __tablename__ = "chatroom_statistic"


class MemberOverview(db.Model):
    __tablename__ = "member_overview"


class MemberStatistic(db.Model):
    __tablename__ = "member_statistic"
