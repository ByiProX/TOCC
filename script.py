# -*- coding: utf-8 -*-
import json
from datetime import timedelta

from configs.config import db
from models.chatroom_member_models import ChatroomInfo, MemberInfo, ChatroomOverview, MemberOverview
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

chatroom_list = db.session.query(ChatroomInfo).all()
for chatroom in chatroom_list:
    member_list = db.session.query(MemberInfo)\
        .filter(MemberInfo.chatroom_id == chatroom.chatroom_id,
                MemberInfo.create_time < (chatroom.create_time + timedelta(minutes = 10))).all()

    for member in member_list:
        member.create_time = chatroom.create_time

db.session.commit()

chatroom_overview_list = db.session.query(ChatroomOverview, ChatroomInfo.chatroomname, ChatroomInfo.create_time).\
    outerjoin(ChatroomInfo, ChatroomOverview.chatroom_id == ChatroomInfo.chatroom_id).all()
for chatroom_overview_row in chatroom_overview_list:
    chatroom_overview = chatroom_overview_row[0]
    chatroomname = chatroom_overview_row[1]
    chatroom_create_time = chatroom_overview_row[2]
    chatroom_overview.chatroomname = chatroomname
    print json.dumps(chatroom_overview.to_json())
    chatroom_overview.batch_update(chatroom_create_time)
    print json.dumps(chatroom_overview.to_json())
    print '---'

db.session.commit()

member_overview_list = db.session.query(MemberOverview, MemberInfo.chatroomname, MemberInfo.username)\
    .outerjoin(MemberInfo, MemberOverview.member_id == MemberInfo.member_id).all()
for member_overview_row in member_overview_list:
    member_overview = member_overview_row[0]
    chatroomname = member_overview_row[1]
    username = member_overview_row[2]
    member_overview.chatroomname = chatroomname
    member_overview.username = username
    print json.dumps(member_overview.to_json())
    member_overview.update_batch()
    print json.dumps(member_overview.to_json())
    print '---'

db.session.commit()

pass
