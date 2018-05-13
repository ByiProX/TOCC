# -*- coding: utf-8 -*-
import logging

from sqlalchemy import desc

from configs.config import db, CONSUMPTION_TASK_TYPE, SUCCESS
from core.auto_reply_core import activate_rule_and_add_task_to_consumption_task
from models.matching_rule_models import GlobalMatchingRule, MatchingRuleInMemory
from models.real_time_quotes_models import RealTimeQuotesDefaultSettingInfo
from utils.u_transformat import str_to_unicode

logger = logging.getLogger('main')


def get_gm_rule_dict():
    """
    获得规则
    :return:
    """
    gm_rule_list = db.session.query(GlobalMatchingRule).filter(GlobalMatchingRule.is_take_effect == 1).order_by(
        desc(GlobalMatchingRule.create_time)).all()

    gm_rule_dict = {}
    for gm_rule in gm_rule_list:
        gm_rule_dict.setdefault(gm_rule.chatroomname, {})
        gm_rule_dict[gm_rule.chatroomname].setdefault(gm_rule.task_type, [])

        gm_rule_dict[gm_rule.chatroomname][gm_rule.task_type]. \
            append(MatchingRuleInMemory(mid=gm_rule.mid,
                                        user_id=gm_rule.user_id,
                                        chatroomname=gm_rule.chatroomname,
                                        match_word=gm_rule.match_word,
                                        task_type=gm_rule.task_type,
                                        task_relevant_id=gm_rule.task_relevant_id,
                                        create_time=gm_rule.create_time,
                                        is_exact_match=gm_rule.is_exact_match))
    return gm_rule_dict


def match_message_by_rule(gm_rule_dict, message_analysis):
    """
    读取目前所有规则，
    :return:
    """
    # 先判断发信息的这个群是否在规则里面，看是否在gm_rule_dict中
    # 如果没有则返回，没什么操作，同样的方法验证gm_rule_dict
    # 如果有，则依次进行匹配，一旦一个分类匹配到，立即停止该匹配，插入任务

    message_chatroomname = message_analysis.talker
    message_text = str_to_unicode(message_analysis.real_content)
    message_said_username = message_analysis.real_talker

    if not message_said_username:
        raise ValueError("没有message_said_username")

    if message_chatroomname not in gm_rule_dict:
        return False

    # 处理自动回复信息
    status_flag = False
    for matching_rule in gm_rule_dict[message_chatroomname][CONSUMPTION_TASK_TYPE['auto_reply']]:
        if matching_rule.is_exact_match and message_text == matching_rule.match_word:
            logger.info(u"匹配到关键词. chatroomname: %s. task_type: %s. task_relevant_id: %s." % (
                message_chatroomname, matching_rule.task_type, matching_rule.task_relevant_id))
            logger.info(u"匹配到关键词. match_word: %s. message_text: %s." % (matching_rule.match_word, message_text))
            status_flag = activate_rule_and_add_task_to_consumption_task(matching_rule.task_relevant_id,
                                                                         message_chatroomname,
                                                                         message_said_username)
            break
        elif not matching_rule.is_exact_match and matching_rule.match_word in message_text:
            logger.info(u"匹配到关键词. chatroomname: %s. task_type: %s. task_relevant_id: %s." % (
                message_chatroomname, matching_rule.task_type, matching_rule.task_relevant_id))
            logger.info(u"匹配到关键词. match_word: %s. message_text: %s." % (matching_rule.match_word, message_text))
            status_flag = activate_rule_and_add_task_to_consumption_task(matching_rule.task_relevant_id,
                                                                         message_chatroomname,
                                                                         message_said_username)
            break
        else:
            pass

    if status_flag is False:
        return False
    if status_flag == SUCCESS:
        return True
    else:
        return status_flag


def get_gm_default_rule_dict():
    """
    获得规则
    :return:
    """

    gm_default_rule_dict = {}
    gm_default_rule_dict.setdefault("is_full_match", {})
    gm_default_rule_dict.setdefault("is_not_full_match", {})

    # 目前先用主表来判断
    rt_quotes_ds_info_list = db.session.query(RealTimeQuotesDefaultSettingInfo).filter(
        RealTimeQuotesDefaultSettingInfo.is_integral == 1).all()
    for rt_quotes_ds_info in rt_quotes_ds_info_list:
        if rt_quotes_ds_info.symbol:
            gm_default_rule_dict["is_full_match"].setdefault(rt_quotes_ds_info.symbol, rt_quotes_ds_info.ds_id)
        else:
            pass

        if rt_quotes_ds_info.coin_name_cn:
            gm_default_rule_dict["is_full_match"].setdefault(rt_quotes_ds_info.coin_name_cn, rt_quotes_ds_info.ds_id)
        else:
            pass
    return gm_default_rule_dict
    #
    # qr_quotes_dkr_info_list = db.session.query(RealTimeQuotesDefaultKeywordRelateInfo).all()
    # for qr_quotes_dkr_info in qr_quotes_dkr_info_list:
    #     if qr_quotes_dkr_info.is_full_match:
    #         gm_default_rule_dict["is_full_match"].setdefault(qr_quotes_dkr_info.keyword, qr_quotes_dkr_info.ds_id)
    #     else:
    #         gm_default_rule_dict["is_not_full_match"].setdefault(qr_quotes_dkr_info.keyword, qr_quotes_dkr_info.ds_id)
    # return gm_default_rule_dict
