# -*- coding: utf-8 -*-
import logging
from decimal import Decimal

from datetime import datetime

from configs.config import db, MAX_MEMBER_COUNT_DECIMAL
from models.android_db_models import AMember, AContact

logger = logging.getLogger("main")


class ChatroomInfo(db.Model):
    """
    一个 Chatroom 只维护一份 info 和 statistic
    chatroom_id: AContact.id
    """
    __tablename__ = "chatroom_info"
    chatroom_id = db.Column(db.BigInteger, primary_key=True)
    chatroomname = db.Column(db.String(32), index=True, unique=True, nullable=False)

    total_speak_count = db.Column(db.BigInteger, index=True, nullable=False)
    total_at_count = db.Column(db.BigInteger, index=True, nullable=False)

    bz_value = db.Column(db.DECIMAL(5, 2), index=True)
    # participative_count = db.Column(db.Integer, index = True)
    # interactive_index = db.Column(db.Float, index = True)
    # participative_index = db.Column(db.Float, index = True)
    # health_index = db.Column(db.Float, index = True)

    # active_count 更新 flag

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    def __init__(self, chatroom_id, chatroomname, member_count, total_speak_count = 0, total_at_count = 0):
        self.chatroom_id = chatroom_id
        self.chatroomname = chatroomname

        self.bz_value = Decimal(member_count) / MAX_MEMBER_COUNT_DECIMAL

        self.total_speak_count = total_speak_count
        self.total_at_count = total_at_count

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

    @staticmethod
    def get_filter_list(filter_list = None, chatroomname = None, username = None, is_on = None):
        if filter_list is None:
            filter_list = list()

        if chatroomname is not None:
            filter_list.append(BotChatroomR.chatroomname == chatroomname)

        if username is not None:
            filter_list.append(BotChatroomR.username == username)

        if is_on is not None:
            filter_list.append(BotChatroomR.is_on == is_on)

        return filter_list


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

    chatroom_id = db.Column(db.BigInteger, index=True, nullable=False)

    speak_count = db.Column(db.BigInteger, index = True, nullable = False)
    be_at_count = db.Column(db.BigInteger, index = True, nullable = False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)
    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    db.UniqueConstraint(chatroomname, username, name='ix_a_member_name')

    @staticmethod
    def fetch_member_by_username(chatroomname, username):
        member = db.session.query(MemberInfo).filter(MemberInfo.chatroomname == chatroomname,
                                                     MemberInfo.username == username).first()
        if not member:
            MemberInfo.update_members()
            # 更新信息之后再查不到就不管了
            member = db.session.query(MemberInfo).filter(MemberInfo.chatroomname == chatroomname,
                                                         MemberInfo.username == username).first()

        return member

    @staticmethod
    def fetch_member_by_nickname(chatroomname, nickname):
        member = None
        if nickname:
            # 匹配 AMember
            a_member = db.session.query(AMember).filter(AMember.displayname == nickname,
                                                        AMember.chatroomname == chatroomname).first()
            if not a_member:
                # 匹配 AContact
                a_contact = db.session.query(AContact).outerjoin(AMember, AMember.username == AContact.username)\
                    .filter(AContact.nickname == nickname, AMember.chatroomname == chatroomname).first()
                if a_contact:
                    member = MemberInfo.fetch_member_by_username(chatroomname, a_contact.username)
                else:
                    logger.error(u"未匹配到 member, nickname: %s, chatroom: %s" % (nickname, chatroomname))
            else:
                member = MemberInfo.fetch_member_by_username(chatroomname, a_member.username)

        return member

    @staticmethod
    def update_members():
        pass


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

    create_time = db.Column(db.DateTime, index=True, nullable=False)


class ChatroomStatistic(db.Model):
    __tablename__ = "chatroom_statistic"
    chatroom_id = db.Column(db.BigInteger, primary_key=True)
    time_to_day = db.Column(db.DateTime, primary_key=True)

    speak_count = db.Column(db.BigInteger, index=True, nullable=False)

    # deprecated
    at_count = db.Column(db.Integer, index=True, nullable=False)

    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    def __init__(self, chatroom_id, time_to_day, speak_count = 0, at_count = 0):
        self.chatroom_id = chatroom_id
        self.time_to_day = time_to_day
        self.speak_count = speak_count
        self.at_count = at_count

    @staticmethod
    def fetch_chatroom_statistics(chatroom_id, time_to_day, create_flag = True, save_flag = True):
        chatroom_statistics = db.session.query(ChatroomStatistic.chatroom_id == chatroom_id,
                                               ChatroomStatistic.time_to_day == time_to_day).first()
        if not chatroom_statistics and create_flag:
            chatroom_statistics = ChatroomStatistic(chatroom_id, time_to_day)
            if save_flag:
                db.session.add(chatroom_statistics)
                db.session.commit()

        return chatroom_statistics


class MemberOverview(db.Model):
    __tablename__ = "member_overview"
    member_id = db.Column(db.BigInteger, primary_key=True)
    scope = db.Column(db.Integer, primary_key=True)

    chatroom_id = db.Column(db.BigInteger, index=True, nullable=False)

    be_at_count = db.Column(db.Integer, index=True, nullable=False)
    speak_count = db.Column(db.Integer, index=True, nullable=False)
    invitation_count = db.Column(db.Integer, index=True, nullable=False)

    red_package_count = db.Column(db.Integer, index=True, nullable=False)
    effect_num = db.Column(db.DECIMAL(5, 2), index=True, nullable=False)

    # active_index = db.Column(db.Float, index = True)
    # importance_index = db.Column(db.Float, index = True)

    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)


class MemberStatistic(db.Model):
    __tablename__ = "member_statistic"
    member_id = db.Column(db.BigInteger, primary_key=True)
    time_to_day = db.Column(db.DateTime, primary_key=True)

    chatroom_id = db.Column(db.BigInteger, index=True, nullable=False)

    be_at_count = db.Column(db.Integer, index=True, nullable=False)
    speak_count = db.Column(db.Integer, index=True, nullable=False)
    invitation_count = db.Column(db.Integer, index=True, nullable=False)

    red_package_count = db.Column(db.Integer, index=True, nullable=False)
    effect_num = db.Column(db.DECIMAL(5, 2), index=True, nullable=False)

    update_time = db.Column(db.TIMESTAMP, index=True, nullable=False)

    def __init__(self, member_id, time_to_day, chatroom_id, be_at_count = 0, speak_count = 0, invitation_count = 0,
                 red_package_count = 0, effect_num = Decimal(u"0")):
        self.member_id = member_id
        self.time_to_day = time_to_day
        self.chatroom_id = chatroom_id

        self.be_at_count = be_at_count
        self.speak_count = speak_count
        self.invitation_count = invitation_count
        self.red_package_count = red_package_count
        self.effect_num = effect_num

    @staticmethod
    def fetch_member_statistics(member_id, time_to_day, chatroom_id, create_flag = True, save_flag = True):
        member_statistics = db.session.query(MemberStatistic.member_id == member_id,
                                             MemberStatistic.time_to_day == time_to_day).first()
        if not member_statistics and create_flag:
            member_statistics = MemberStatistic(member_id, time_to_day, chatroom_id)
            if save_flag:
                db.session.add(member_statistics)
                db.session.commit()

        return member_statistics
