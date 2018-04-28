# -*- coding: utf-8 -*-
import json
import logging
import time
from datetime import timedelta, datetime

from sqlalchemy import func, or_

from configs.config import db, USER_CHATROOM_R_PERMISSION_1, GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG, \
    GLOBAL_RULES_UPDATE_FLAG, GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG, MSG_TYPE_TXT, MSG_TYPE_SYS, UserBotR, Contact
from core_v2.matching_rule_core import get_gm_rule_dict, get_gm_default_rule_dict
from core_v2.message_core import route_msg
from core_v2.user_core import _get_a_balanced_bot
from crawler.coin_all_crawler_v2 import update_coin_all

from models_v2.base_model import CM, BaseModel
from utils.u_model_json_str import model_to_dict

logger = logging.getLogger('main')

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
from models.qun_friend_models import UserQunBotRelateInfo, UserQunRelateInfo, GroupInfo
from models.user_bot_models import UserBotRelateInfo, BotInfo, UserInfo

from utils.u_time import get_today_0, datetime_to_timestamp_utc_8


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
        user_chatroom_r = db.session.query(UserChatroomR).filter(UserChatroomR.user_id == user_id,
                                                                 UserChatroomR.chatroom_id == a_contact_chatroom.id).first()
        if user_chatroom_r:
            user_chatroom_r.permission = USER_CHATROOM_R_PERMISSION_1
        else:
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


def init_count_msg():
    start_time = datetime(year = 2017, month = 3, day = 24, hour = 14, minute = 19, second = 1)
    end_time = datetime(year = 2018, month = 3, day = 24, hour = 14, minute = 19, second = 1)
    count_msg_by_create_time(start_time, end_time)


def clear_all_user_data():
    user_id_list = [3]
    for user_id in user_id_list:
        print user_id
        # user_info
        user_info_list = db.session.query(UserInfo).filter(UserInfo.user_id == user_id).all()

        # user_qun_relate_info
        uqr_list = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == user_id).all()
        uqun_ids = [r.uqun_id for r in uqr_list]

        # user_bot_relate_info
        ubr_list = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_id).all()
        user_bot_rids = [r.user_bot_rid for r in ubr_list]

        # user_qun_bot_relate_info
        uqbr_list = db.session.query(UserQunBotRelateInfo).filter(or_(UserQunBotRelateInfo.uqun_id.in_(uqun_ids),
                                                                      UserQunBotRelateInfo.user_bot_rid.in_(user_bot_rids)))

        # user_chatroom_r
        ucr_list = db.session.query(UserChatroomR).filter(UserChatroomR.user_id == user_id).all()

        # synchronous_announcement_ds_user_relate
        sadsur_list = db.session.query(SynchronousAnnouncementDSUserRelate).filter(SynchronousAnnouncementDSUserRelate.user_id == user_id).all()

        # material_library_user
        mlu_list = db.session.query(MaterialLibraryUser).filter(MaterialLibraryUser.user_id == user_id).all()

        # group_info
        gi_list = db.session.query(GroupInfo).filter(GroupInfo.user_id == user_id).all()

        # global_matching_rule
        gmr_list = db.session.query(GlobalMatchingRule).filter(GlobalMatchingRule.user_id == user_id).all()

        # coin_wallet_qun_member_relate
        cwqmr_list = db.session.query(CoinWalletQunMemberRelate).filter(CoinWalletQunMemberRelate.user_id == user_id).all()
        uqun_member_ids = [r.uqun_member_id for r in cwqmr_list]

        # coin_wallet_member_address_relate
        cwmar_list = db.session.query(CoinWalletMemberAddressRelate).filter(CoinWalletMemberAddressRelate.uqun_member_id.in_(uqun_member_ids)).all()

        # batch_sending_task_info
        bsti_list = db.session.query(BatchSendingTaskInfo).filter(BatchSendingTaskInfo.user_id == user_id).all()
        sending_task_ids = [r.sending_task_id for r in bsti_list]

        # batch_sending_task_material_relate
        bstmr_list = db.session.query(BatchSendingTaskMaterialRelate).filter(BatchSendingTaskMaterialRelate.sending_task_id.in_(sending_task_ids)).all()

        # batch_sending_task_target_relate
        bsttr_list = db.session.query(BatchSendingTaskTargetRelate).filter(BatchSendingTaskTargetRelate.sending_task_id.in_(sending_task_ids)).all()

        # auto_reply_setting_info
        arsi_list = db.session.query(AutoReplySettingInfo).filter(AutoReplySettingInfo.user_id == user_id).all()
        setting_ids = [r.setting_id for r in arsi_list]

        # auto_reply_keyword_relate_Info
        arkri_list = db.session.query(AutoReplyKeywordRelateInfo).filter(AutoReplyKeywordRelateInfo.setting_id.in_(setting_ids)).all()

        # auto_reply_material_relate
        armr_list = db.session.query(AutoReplyMaterialRelate).filter(AutoReplyMaterialRelate.setting_id.in_(setting_ids)).all()

        # auto_reply_target_relate
        artr_list = db.session.query(AutoReplyTargetRelate).filter(AutoReplyTargetRelate.setting_id.in_(setting_ids)).all()

        session_delete(user_info_list)
        session_delete(uqr_list)
        session_delete(ubr_list)
        session_delete(uqbr_list)
        session_delete(ucr_list)
        session_delete(sadsur_list)
        session_delete(mlu_list)
        session_delete(gi_list)
        session_delete(gmr_list)
        session_delete(cwqmr_list)
        session_delete(cwmar_list)
        session_delete(bsti_list)
        session_delete(bstmr_list)
        session_delete(bsttr_list)
        session_delete(arsi_list)
        session_delete(arkri_list)
        session_delete(armr_list)
        session_delete(artr_list)
        db.session.commit()


def session_delete(li):
    for l in li:
        db.session.delete(l)


def test_msg(message_list):
    # 第一次读取用户设置词
    gm_rule_dict = get_gm_rule_dict()
    GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = False

    # 第一次读取统一设置词
    gm_default_rule_dict = get_gm_default_rule_dict()
    GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG] = False

    message_analysis_list = list()
    # if len(message_list) != 0:
    #     ProductionThread._process_a_msg_list(message_list, message_analysis_list)
    if len(message_list) != 0:
        for i, a_message in enumerate(message_list):
            message_analysis = analysis_and_save_a_message(a_message)
            if not message_analysis:
                continue
            message_analysis_list.append(message_analysis)

            # 判断这个机器人说的话是否是文字或系统消息
            if message_analysis.type == MSG_TYPE_TXT or message_analysis.type == MSG_TYPE_SYS:
                pass
            else:
                continue

            # 这个机器人说的话
            if message_analysis.is_send == 1:
                continue

            # is_add_friend
            # is_add_friend = check_whether_message_is_add_friend(message_analysis)
            # if is_add_friend:
            #     continue

            # 检查信息是否为加了一个群
            is_add_qun = check_whether_message_is_add_qun(message_analysis)
            if is_add_qun:
                continue

            # is_removed
            is_removed = check_is_removed(message_analysis)
            if is_removed:
                continue

            # is_a_coin_wallet
            is_a_coin_wallet = check_whether_message_is_a_coin_wallet(message_analysis)
            if is_a_coin_wallet:
                continue

            # 检测是否是别人的进群提示
            is_friend_into_qun = check_whether_message_is_friend_into_qun(message_analysis)

            # 根据规则和内容进行匹配，并生成任务
            rule_status = match_message_by_rule(gm_rule_dict, message_analysis)
            if rule_status is True:
                continue
            else:
                pass

            # 对内容进行判断，是否为查询比价的情况
            coin_price_status = match_message_by_coin_keyword(gm_default_rule_dict, message_analysis)
            if coin_price_status is True:
                continue


# if __name__ == '__main__':
    # update_member_overview()
    # init_cia()
    # init_count_msg()
    # clear_all_user_data()


if __name__ == '__main__':
    BaseModel.extract_from_json()
    username_list = ["wxid_u391xytt57gc21"] * 500
    a_contact = BaseModel.fetch_all("a_contact", "*", BaseModel.where("in", "username", username_list))
    # update_coin_all()
    # BaseModel.fetch_all('sensitive_message_log', '*',
    #                     BaseModel.and_([">", "create_time", 1524733303],
    #                                    ["<", "create_time", 1524733305]), page = 1, pagesize = 1)
    # pass
    # exit()
    # coins = BaseModel.fetch_all("coin", "*")
    # pass
    # exit()
    # uqr = BaseModel.fetch_by_id("client_qun_r", "5ad46153f5d7e26589658ba7")
    # uqr.group_id = u"4_0"
    # uqr.update()
    # message_json = {u'status': 3, u'msg_local_id': u'116', u'is_send': 0, u'reserved': u'', u'msg_svr_id': None,
    #                 u'bot_username': u'wxid_3mxn5zyskbpt22', u'is_at': None, u'is_to_friend': 0,
    #                 u'content': u'wxid_u391xytt57gc21:\nbtc', u'create_time': 1523872665000,
    #                 u'talker': u'4648276167@chatroom', u'real_content': u'btc',
    #                 u'real_talker': u'wxid_u391xytt57gc21', u'type': 1}
    # a_message = CM("a_message").from_json(message_json)
    # gm_rule_dict = get_gm_rule_dict()
    # gm_default_rule_dict = get_gm_default_rule_dict()
    # route_msg(a_message, gm_rule_dict, gm_default_rule_dict)
    # ubr = CM(UserBotR)
    # ubr.client_id = 1
    # ubr.bot_username = u'wxid_zy8gemkhx2r222'
    # ubr.is_work = 1
    # ubr.create_time = int(time.time())
    # ubr.save()
    # now_time = datetime_to_timestamp_utc_8(datetime.now())
    # client = BaseModel.fetch_by_id(u"client", 1)
    # client.save()
    # client.client_id = int(client.client_id)
    # client.create_time = long(client.create_time)
    # client.update_time = long(client.update_time)
    # client.client_name = u"Doodod"
    # client.client_cn_name = u"独到科技"
    # client.tel = u"18888888888"
    # client.admin = u"neil"
    # client.update_time = datetime_to_timestamp_utc_8(datetime.now())
    # client.save()
    # # user_list = db.session.query(UserInfo).all()
    #
    # # user_old = db.session.query(UserInfo).filter(UserInfo.user_id == 5).first()
    # # user_old_json = model_to_dict(user_old, user_old.__class__)
    # # user_old_json['client_id'] = 1
    # # user_old_json['last_login_time'] = int(user_old_json['last_login_time']) / 1000
    # # user_old_json['token_expired_time'] = int(user_old_json['token_expired_time']) / 1000
    # # user_old_json['create_time'] = int(user_old_json['create_time']) / 1000
    # # user = CM("client_member").from_json(user_old_json)
    # # user_switch = CM('client_switch').from_json(user_old_json)
    # # user.code = "111"
    # # user.token = "222"
    # # user.save()
    # # user_switch.save()
    #
    # contact = CM(Contact)
    # contact.username = u"wxid_3mxn5zyskbpt22"
    # contact.nickname = u"柳罗"
    # contact.quan_pin = u"liuluo"
    # contact.py_initial = u"ll"
    # contact.contact_label_ids = u""
    # contact.avatar_url = u"http://wx.qlogo.cn/mmhead/ver_1/MSznWf00lhxtibw2TbbNQEt6fLp7dicMWfo0ITBTWz3vwb2WLGuYkE6EKdxL7GSjlYXqboJl7LLmE8k1g2XEC3otk4cx5ChNBYS6icnGvXql0s/132"
    # contact.img_lastupdatetime = now_time
    # contact.create_time = now_time
    # contact.update_time = now_time
    # contact.province = u"北京"
    # contact.city = u"海淀"
    # contact.sex = 1
    # contact.signature = u""
    # contact.save()
    #
    # bot_info = CM(BotInfo)
    # bot_info.username = u"wxid_3mxn5zyskbpt22"
    # bot_info.create_bot_time = now_time
    # bot_info.is_alive = 1
    # bot_info.alive_detect_time = now_time
    # bot_info.save()
    #
    # ubr = CM(UserBotR)
    # ubr.client_id = client.client_id
    # ubr.bot_username = bot_info.username
    # ubr.chatbot_default_nickname = u"奔跑的小黄豆"
    # ubr.is_work = 1
    # ubr.create_time = now_time
    # ubr.save()
    # # for user in user_list:
    # #     client = CM('client')
    # #     client.create_time = datetime_to_timestamp_utc_8(datetime.now())
    # #     client.client_name = user.open_id
    # #     client.admin = user.open_id
    # #     client.save()
    # #     user_json = model_to_dict(user, user.__class__)
    # #     user_json['client_id'] = client.client_id
    # #     user_json['open_id'] += "a"
    # #     user_json['last_login_time'] = int(user_json['last_login_time']) / 1000
    # #     user_json['token_expired_time'] = int(user_json['token_expired_time']) / 1000
    # #     user_json['create_time'] = int(user_json['create_time']) / 1000
    # #     user_info = CM('client_member').from_json(user_json)
    # #     user_switch = CM('client_switch').from_json(user_json)
    # #     user_info.save()
    # #     user_switch.save()
    # # user_info_list = BaseModel.fetch_all('client_member', "*", order_by = BaseModel.order_by({"union_id": "desc"}))
    # # user_info = BaseModel.fetch_by_id(u'client_member', u'5acb919f421aa9393f212b88')
    # # user_info.union_id = "1"
    # # user_info.update()
    #
    # chatroomname = u"5437479256@chatroom"
    # chatroom_info = db.session.query(AChatroom).filter(AChatroom.chatroomname == chatroomname).first()
    # chatroom_info_json = model_to_dict(chatroom_info, chatroom_info.__class__)
    # a_contact_chatroom = db.session.query(AContact).filter(AContact.username == chatroomname).first()
    # a_contact_chatroom_json = model_to_dict(a_contact_chatroom, a_contact_chatroom.__class__)
    # chatroom = CM("a_chatroom")
    # chatroom.from_json(chatroom_info_json)
    # chatroom.from_json(a_contact_chatroom_json)
    # chatroom.member_count = 5
    #
    # member = CM("a_member")
    # member_list = list()
    #
    # friend_info = CM("a_friend")
    # friend_info.bot_username = u"wxid_3mxn6zyskbpt22"
    #
    # to_username_list = list()
    # rows = db.session.query(AMember, AContact).outerjoin(AContact, AMember.username == AContact.username).filter(AMember.chatroomname == chatroomname).all()
    # for row in rows:
    #     member_dict = dict()
    #     a_member = row[0]
    #     to_username_list.append(a_member.username)
    #     a_contact = row[1]
    #     member_dict["username"] = a_member.username
    #     member_dict["displayname"] = a_member.displayname
    #     member_dict["is_deleted"] = 0
    #     member_list.append(member_dict)
    #     a_contact_json = model_to_dict(a_contact, a_contact.__class__)
    #     a_contact_json["create_time"] = int(a_contact_json["create_time"]) / 1000
    #     a_contact_json["update_time"] = int(a_contact_json["update_time"]) / 1000
    #     a_contact_json["avatar_url"] = a_contact_json["avatar_url2"]
    #     contact = CM("a_contact")
    #     contact.from_json(a_contact_json)
    #     contact.save()
    #
    # friend_list = list()
    # friends = db.session.query(AFriend).filter(AFriend.from_username == u"wxid_6mf4yqgs528e22",
    #                                            AFriend.to_username.in_(to_username_list)).all()
    # for friend in friends:
    #     # friend_dict = model_to_dict(friend, friend.__class__)
    #     friend_dict = dict()
    #     friend_dict['username'] = friend.to_username
    #     friend_dict['con_remark'] = friend.con_remark
    #     friend_dict['con_remark_py_full'] = friend.con_remark_py_full
    #     friend_dict['con_remark_py_short'] = friend.con_remark_py_short
    #     friend_dict['type'] = friend.type
    #     friend_dict["create_time"] = datetime_to_timestamp_utc_8(friend.create_time)
    #     friend_dict["update_time"] = datetime_to_timestamp_utc_8(friend.update_time)
    #     friend_list.append(friend_dict)
    # friend_info.friends = friend_list
    # friend_info.save()
    # member.chatroomname = chatroomname
    # member.members = member_list
    #
    # chatroom.nickname_real = chatroom.nickname
    # chatroom.avatar_url = a_contact_chatroom.avatar_url2
    # chatroom.create_time = int(chatroom.create_time) / 1000
    # chatroom.update_time = int(chatroom.update_time) / 1000
    # print json.dumps(chatroom.to_json_full())
    # print json.dumps(member.to_json_full())
    # chatroom.save()
    # member.save()
    # # exit()
    #
    # # message_list = db.session.query(MessageAnalysis).filter(MessageAnalysis.msg_id == 20420).all()
    # # for message in message_list:
    # #     message.username = u"wxid_3mxn6zyskbpt22"
    # #     print message.msg_id, message.content
    # #     msg_json = model_to_dict(message, message.__class__)
    # #     msg_json["bot_username"] = msg_json["username"]
    # #     response = requests.post("http://127.0.0.1:5505/yaca_api_v2/android/new_message", json = msg_json)
    pass

pass
