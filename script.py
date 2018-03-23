# -*- coding: utf-8 -*-
import json
from datetime import timedelta, datetime

from sqlalchemy import func

from configs.config import db
from models.android_db_models import AMember, AContact
from models.chatroom_member_models import ChatroomInfo, MemberInfo, ChatroomOverview, MemberOverview, ChatroomStatistic
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
    member_overview_list = db.session.query(MemberOverview).all()
    for member_overview in member_overview_list:
        print json.dumps(member_overview.to_json())
        member_overview.update_batch()
        print json.dumps(member_overview.to_json())
        print '---'

    db.session.commit()
    del member_overview_list


if __name__ == '__main__':
    update_member_overview()

pass
