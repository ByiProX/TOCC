import json

from configs.config import db
from models.chatroom_member_models import ChatroomOverview, ChatroomInfo, MemberOverview, MemberInfo, ChatroomStatistic


def update_chatroom_overview():
    chatroom_overview_list = db.session.query(ChatroomOverview, ChatroomInfo.create_time).\
        outerjoin(ChatroomInfo, ChatroomOverview.chatroom_id == ChatroomInfo.chatroom_id).all()
    for chatroom_overview_row in chatroom_overview_list:
        chatroom_overview = chatroom_overview_row[0]
        chatroom_create_time = chatroom_overview_row[1]
        # print json.dumps(chatroom_overview.to_json())
        chatroom_overview.batch_update(chatroom_create_time)
        # print json.dumps(chatroom_overview.to_json())
        # print '---'

    db.session.commit()
    del chatroom_overview_list


def update_member_overview():
    member_overview_list = db.session.query(MemberOverview).all()
    for member_overview in member_overview_list:
        # print json.dumps(member_overview.to_json())
        member_overview.update_batch()
        # print json.dumps(member_overview.to_json())
        # print '---'

    db.session.commit()
    del member_overview_list


def update_chatroom_statistics():
    chatroom_statistics_list = db.session.query(ChatroomStatistic).all()
    for chatroom_statistics in chatroom_statistics_list:
        chatroom_statistics.update_all_member_count()

    db.session.commit()
    del chatroom_statistics_list


update_chatroom_overview()
