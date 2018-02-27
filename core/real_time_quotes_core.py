# -*- coding: utf-8 -*-

import logging

from datetime import datetime

from configs.config import ERR_WRONG_FUNC_STATUS, db, SUCCESS, ERR_WRONG_ITEM, CONSUMPTION_TASK_TYPE, TASK_SEND_TYPE, \
    ERR_WRONG_USER_ITEM
from models.production_consumption_models import ConsumptionTask
from models.qun_friend_models import UserQunRelateInfo, UserQunBotRelateInfo
from models.real_time_quotes_models import RealTimeQuotesDSUserRelate, RealTimeQuotesDefaultSettingInfo
from models.user_bot_models import UserBotRelateInfo, BotInfo
from utils.u_str_unicode import str_to_unicode

logger = logging.getLogger('main')


def switch_func_real_time_quotes(user_info, switch):
    """
    打开或关闭实时报价功能
    :param user_info:
    :param switch:
    :return:
    """
    if user_info.func_real_time_quotes and switch:
        logger.error("目前已为开启状态，无需再次开启")
        return ERR_WRONG_FUNC_STATUS
    if not user_info.func_real_time_quotes and not switch:
        logger.error("目前已为关闭状态，无需再次开启")
        return ERR_WRONG_FUNC_STATUS

    if switch is True:
        rt_quotes_ds_info_list = db.session.query(RealTimeQuotesDefaultSettingInfo).all()
        for rt_quotes_ds_info in rt_quotes_ds_info_list:
            rt_quotes_dsu_rel = RealTimeQuotesDSUserRelate()
            rt_quotes_dsu_rel.ds_id = rt_quotes_ds_info.ds_id
            rt_quotes_dsu_rel.user_id = user_info.user_id
            rt_quotes_dsu_rel.create_time = datetime.now()
            db.session.add(rt_quotes_dsu_rel)
        user_info.func_real_time_quotes = True
        db.session.commit()
    elif switch is False:
        rt_quotes_dsu_rel_list = db.session.query(RealTimeQuotesDSUserRelate).filter(
            RealTimeQuotesDSUserRelate.user_id == user_info.user_id).all()

        for rt_quotes_dsu_rel in rt_quotes_dsu_rel_list:
            db.session.delete(rt_quotes_dsu_rel)

        user_info.func_real_time_quotes = False
        db.session.commit()

    return SUCCESS


def match_message_by_coin_keyword(gm_default_rule_dict, message_analysis):
    is_match_coin_keyword = False
    message_chatroomname = message_analysis.talker
    message_text = str_to_unicode(message_analysis.real_content)
    message_said_username = message_analysis.real_talker

    if not message_said_username:
        raise ValueError("没有message_said_username")

    if message_text in gm_default_rule_dict['is_full_match']:
        # 已经匹配到了text，执行后续操作
        activate_rule_and_add_task_to_consumption_task(gm_default_rule_dict['is_full_match'][message_text],
                                                       message_chatroomname, message_said_username)
        is_match_coin_keyword = True
        pass

    for keyword, ds_id in gm_default_rule_dict['is_not_full_match']:
        if keyword in message_text:
            activate_rule_and_add_task_to_consumption_task(gm_default_rule_dict['is_not_full_match'][message_text],
                                                           message_chatroomname, message_said_username)
            is_match_coin_keyword = True

    return is_match_coin_keyword


def activate_rule_and_add_task_to_consumption_task(ds_id, message_chatroomname, message_said_username):
    ds_info = db.session.query(RealTimeQuotesDefaultSettingInfo).filter(ds_id).first()
    if not ds_info:
        return ERR_WRONG_ITEM

    uqr_info_list = db.session.query(UserQunRelateInfo).filter(
        UserQunRelateInfo.chatroomname == message_chatroomname).all()
    if not uqr_info_list:
        logger.error("没有符合该群的机器人及用户")
        return ERR_WRONG_ITEM
    chatroom_relate_user_id_dict = {}
    for uqr_info in uqr_info_list:
        chatroom_relate_user_id_dict.setdefault(uqr_info.user_id, uqr_info)

    rt_quotes_dsu_relate_list = db.session.query(RealTimeQuotesDSUserRelate).filter(
        RealTimeQuotesDSUserRelate.ds_id == ds_id).all()
    for rt_quotes_dsu_relate in rt_quotes_dsu_relate_list:
        if rt_quotes_dsu_relate.user_id in chatroom_relate_user_id_dict:
            c_task = ConsumptionTask()
            c_task.qun_owner_user_id = rt_quotes_dsu_relate.user_id
            c_task.task_initiate_user_id = rt_quotes_dsu_relate.user_id

            c_task.chatroomname = chatroom_relate_user_id_dict[rt_quotes_dsu_relate.user_id].chatroomname
            c_task.task_type = CONSUMPTION_TASK_TYPE['real_time_quotes']
            c_task.task_relevant_id = ds_id

            c_task.task_send_type = TASK_SEND_TYPE['text']

            c_task.task_send_content = message_said_username + u"这里是币的信息"

            uqun_id = chatroom_relate_user_id_dict[rt_quotes_dsu_relate.user_id].uqun_id

            uqbr_info_list = db.session.query(UserQunBotRelateInfo).filter(
                UserQunBotRelateInfo.uqun_id == uqun_id).all()
            if not uqbr_info_list:
                logger.error(u"没有找到群与机器人绑定关系. qun_id: %s." % uqun_id)
                return ERR_WRONG_USER_ITEM
            user_bot_rid_list = []
            for uqbr_info in uqbr_info_list:
                if uqbr_info.is_error is True:
                    continue
                else:
                    user_bot_rid_list.append(uqbr_info.user_bot_rid)
            # 目前只要读取到一个bot_id就好
            bot_id = None
            for user_bot_rid in user_bot_rid_list:
                ubr_info = db.session.query(UserBotRelateInfo).filter(
                    UserBotRelateInfo.user_bot_rid == user_bot_rid).all()
                bot_id = ubr_info[0].bot_id
                if bot_id:
                    break

            bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == bot_id).first()
            if not bot_info:
                logger.error(u"没有找到bot相关信息. bot_id: %s." % bot_id)
                return ERR_WRONG_ITEM

            c_task.bot_username = bot_info.username
            now_time = datetime.now()
            c_task.message_received_time = now_time
            c_task.task_create_time = now_time

            db.session.add(c_task)
            db.session.commit()
            return SUCCESS
