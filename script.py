# -*- coding: utf-8 -*-
import json
from datetime import timedelta, datetime

from sqlalchemy import func

from configs.config import db, USER_CHATROOM_R_PERMISSION_1
from core.message_core import update_members
from models.android_db_models import AMember, AContact, AChatroomR
from models.chatroom_member_models import ChatroomInfo, MemberInfo, ChatroomOverview, MemberOverview, ChatroomStatistic, \
    UserChatroomR, BotChatroomR
from models.message_ext_models import MessageAnalysis

# i = 300
# while i < 67240:
#     MessageAnalysis.count_msg_by_ids(i, i + 100)
#     i += 300

# len_wechats = len(wechats)
# i = 1
# for wechat in wechats:
#     wechat_id = wechat.id
#     logger.info('wechat_id: ' + str(wechat_id) + ' | ' + str(i) + ' / ' + str(len_wechats))
#     i += 1

# chatroom_list = db.session.query(ChatroomInfo).all()
# for chatroom in chatroom_list:
#     member_list = db.session.query(MemberInfo)\
#         .filter(MemberInfo.chatroom_id == chatroom.chatroom_id,
#                 MemberInfo.create_time < (chatroom.create_time + timedelta(minutes = 10))).all()
#
#     for member in member_list:
#         member.create_time = chatroom.create_time
#
# db.session.commit()

# chatroom_overview_list = db.session.query(ChatroomOverview, ChatroomInfo.create_time).\
#     outerjoin(ChatroomInfo, ChatroomOverview.chatroom_id == ChatroomInfo.chatroom_id).all()
# for chatroom_overview_row in chatroom_overview_list:
#     chatroom_overview = chatroom_overview_row[0]
#     chatroom_create_time = chatroom_overview_row[1]
#     print json.dumps(chatroom_overview.to_json())
#     chatroom_overview.batch_update(chatroom_create_time)
#     print json.dumps(chatroom_overview.to_json())
#     print '---'
#
# db.session.commit()


# member_overview_list = db.session.query(MemberOverview).filter(MemberOverview.member_id == 4596619).all()
# for member_overview_row in member_overview_list:
#     member_overview = member_overview_row
#     print json.dumps(member_overview.to_json())
#     member_overview.update_batch()
#     print json.dumps(member_overview.to_json())
#     print '---'
#
# db.session.commit()
from models.qun_friend_models import UserQunBotRelateInfo, UserQunRelateInfo
from models.user_bot_models import UserBotRelateInfo, BotInfo

from utils.u_time import get_today_0

# chatroom_statistics_list = db.session.query(ChatroomStatistic).all()
# for chatroom_statistics in chatroom_statistics_list:
#     chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroom_id == chatroom_statistics.chatroom_id).first()
#     chatroom_create_time = chatroom.create_time
#     start_time = chatroom_statistics.time_to_day
#     time_gap = timedelta(days = 1)
#     end_time = start_time + time_gap
#     filter_list_total = AMember.get_filter_list(chatroomname = chatroom.chatroomname, is_deleted = False,
#                                                 end_time = end_time)
#     filter_list_total.append(AContact.id > 0)
#     filter_list_in = AMember.get_filter_list(chatroomname = chatroom.chatroomname, is_deleted = False,
#                                              start_time = start_time, end_time = end_time)
#     filter_list_in.append(AMember.create_time > chatroom.create_time)
#     filter_list_in.append(AContact.id > 0)
#     filter_list_out = AMember.get_filter_list(chatroomname = chatroom.chatroomname, is_deleted = True,
#                                               start_time = start_time, end_time = end_time)
#     filter_list_out.append(AContact.id > 0)
#     members_in = db.session.query(func.count(AMember.id)) \
#                      .outerjoin(AContact, AMember.username == AContact.username) \
#                      .filter(*filter_list_in).first()[0] or 0
#     members_out = db.session.query(func.count(AMember.id)) \
#                       .outerjoin(AContact, AMember.username == AContact.username) \
#                       .filter(*filter_list_out).first()[0] or 0
#     member_count = db.session.query(func.count(AMember.id)) \
#                        .outerjoin(AContact, AMember.username == AContact.username) \
#                        .filter(*filter_list_total).first()[0] or 0
#     chatroom_statistics.in_count = members_in
#     chatroom_statistics.out_count = members_out
#     chatroom_statistics.member_count = member_count

# db.session.commit()


def update_member_overview():
    i = 0
    member_overview_list = db.session.query(MemberOverview).order_by(MemberOverview.member_id.desc()).all()
    for member_overview in member_overview_list:
        print json.dumps(member_overview.to_json())
        member_overview.update_batch()
        print json.dumps(member_overview.to_json())
        print '---'
        i += 1
        if i % 5000 == 0:
            db.session.commit()
    db.session.commit()
    del member_overview_list


def init_cia():
    uqb_r_list = db.session.query(UserQunBotRelateInfo).filter(UserQunBotRelateInfo.is_error == False).all()
    for uqb_r in uqb_r_list:
        uqun_r = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.uqun_id == uqb_r.uqun_id).first()
        a_contact_chatroom = db.session.query(AContact).filter(AContact.username == uqun_r.chatroomname).first()
        user_bot_r = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_bot_rid == uqb_r.user_bot_rid).first()
        bot = db.session.query(BotInfo).filter(BotInfo.bot_id == user_bot_r.bot_id).first()
        a_chatroom_r = db.session.query(AChatroomR).filter(AChatroomR.username == bot.username,
                                                           AChatroomR.chatroomname == a_contact_chatroom.username).first()

        now = datetime.now()
        user_id = user_bot_r.user_id
        chatroomname = a_contact_chatroom.username
        # chatroom
        chatroom = ChatroomInfo(chatroom_id = a_contact_chatroom.id, chatroomname = chatroomname,
                                member_count = a_contact_chatroom.member_count).generate_create_time(now)
        db.session.merge(chatroom)

        # user_chatroom_r
        user_chatroom_r = UserChatroomR(user_id = user_id, chatroom_id = a_contact_chatroom.id,
                                        permission = USER_CHATROOM_R_PERMISSION_1) \
            .generate_create_time(now)
        db.session.add(user_chatroom_r)

        # bot_chatroom_r
        # 判断是否已经有 is_on 状态的其他 bot
        is_on = True
        bot_chatroom_r_is_on = db.session.query(BotChatroomR).filter(BotChatroomR.chatroomname == chatroomname,
                                                                     BotChatroomR.is_on == 1).first()
        if bot_chatroom_r_is_on:
            is_on = False
        bot_chatroom_r = BotChatroomR(a_chatroom_r_id = a_chatroom_r.id, chatroomname = a_chatroom_r.chatroomname,
                                      username = a_chatroom_r.username, is_on = is_on).generate_create_time(now)
        db.session.merge(bot_chatroom_r)

        # 初始化 MemberInfo 和 MemberOverview
        update_members(chatroomname, create_time = now)

        # 初始化 ChatroomOverview
        ChatroomOverview.init_all_scope(chatroom_id = a_contact_chatroom.id,
                                        chatroomname = a_contact_chatroom.username)

        db.session.commit()


if __name__ == '__main__':
    # update_member_overview()
    init_cia()

pass
