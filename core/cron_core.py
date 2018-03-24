# -*- coding: utf-8 -*-

from configs.config import db
from core.chatroom_member_core import update_all_member_count, batch_update_chatroom_overview, \
    batch_update_member_overview
from models.chatroom_member_models import ChatroomOverview, ChatroomInfo, MemberOverview, ChatroomStatistic


def update_chatroom_overview():
    chatroom_overview_list = db.session.query(ChatroomOverview, ChatroomInfo.create_time).\
        outerjoin(ChatroomInfo, ChatroomOverview.chatroom_id == ChatroomInfo.chatroom_id).all()
    for chatroom_overview_row in chatroom_overview_list:
        chatroom_overview = chatroom_overview_row[0]
        chatroom_create_time = chatroom_overview_row[1]
        # print json.dumps(chatroom_overview.to_json())
        batch_update_chatroom_overview(chatroom_overview, chatroom_create_time)
        # print json.dumps(chatroom_overview.to_json())
        # print '---'

    db.session.commit()
    del chatroom_overview_list


def update_member_overview():
    i = 0
    member_overview_list = db.session.query(MemberOverview).order_by(MemberOverview.member_id.desc()).all()
    for member_overview in member_overview_list:
        chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroom_id == member_overview.chatroom_id)\
            .first()
        # print json.dumps(member_overview.to_json())
        batch_update_member_overview(member_overview, chatroom.create_time)
        # print json.dumps(member_overview.to_json())
        # print '---'
        i += 1
        if i % 5000 == 0:
            db.session.commit()
    db.session.commit()
    del member_overview_list


def update_chatroom_statistics():
    chatroom_statistics_list = db.session.query(ChatroomStatistic).all()
    for chatroom_statistics in chatroom_statistics_list:
        update_all_member_count(chatroom_statistics)

    db.session.commit()
    del chatroom_statistics_list


# update_chatroom_statistics()
# update_chatroom_overview()
