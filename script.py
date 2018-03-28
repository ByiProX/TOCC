# -*- coding: utf-8 -*-
import json
import logging
from datetime import timedelta, datetime

from sqlalchemy import func, or_

from configs.config import db, USER_CHATROOM_R_PERMISSION_1, GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG, \
    GLOBAL_RULES_UPDATE_FLAG, GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG, MSG_TYPE_TXT, MSG_TYPE_SYS
from core.coin_wallet_core import check_whether_message_is_a_coin_wallet
from core.matching_rule_core import get_gm_rule_dict, get_gm_default_rule_dict, match_message_by_rule
from core.message_core import update_members, count_msg_by_create_time, analysis_and_save_a_message
from core.qun_manage_core import check_whether_message_is_add_qun, check_is_removed
from core.real_time_quotes_core import match_message_by_coin_keyword
from core.welcome_message_core import check_whether_message_is_friend_into_qun
from models.android_db_models import AMember, AContact, AChatroomR
from models.auto_reply_models import AutoReplySettingInfo, AutoReplyKeywordRelateInfo, AutoReplyMaterialRelate, \
    AutoReplyTargetRelate
from models.batch_sending_models import BatchSendingTaskInfo, BatchSendingTaskMaterialRelate, \
    BatchSendingTaskTargetRelate
from models.chatroom_member_models import ChatroomInfo, MemberInfo, ChatroomOverview, MemberOverview, ChatroomStatistic, \
    UserChatroomR, BotChatroomR
from models.coin_wallet_models import CoinWalletQunMemberRelate, CoinWalletMemberAddressRelate
from models.matching_rule_models import GlobalMatchingRule
from models.material_library_models import MaterialLibraryUser
from models.message_ext_models import MessageAnalysis
from models.synchronous_announcement_models import SynchronousAnnouncementDSUserRelate

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
            # TODO 当有两个机器人的时候，这里不仅要判断是否是自己说的，还是要判断是否是其他机器人说的
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


if __name__ == '__main__':
    # update_member_overview()
    # init_cia()
    # init_count_msg()
    clear_all_user_data()

pass
