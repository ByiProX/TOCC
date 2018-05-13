# -*- coding: utf-8 -*-
import logging

from configs.config import SUCCESS, Keywords, Coin
from core_v2.send_msg import send_msg_to_android
from models_v2.base_model import BaseModel
from utils.u_transformat import str_to_unicode

logger = logging.getLogger('main')


def get_gm_rule_dict():
    """
    获得规则
    :return:
    """

    keywords_list = BaseModel.fetch_all(Keywords, "*", where_clause = BaseModel.where_dict({"welcome": 0,
                                                                                            "status": 1}))
    gm_rule_dict = {}
    for keywords_info in keywords_list:
        for chatroomname in keywords_info.chatroom_list:
            gm_rule_dict.setdefault(chatroomname, list())
            gm_rule_dict[chatroomname].append({"reply_content": keywords_info.reply_content,
                                               "keywords": keywords_info.keywords})
    return gm_rule_dict


def match_message_by_rule(gm_rule_dict, a_message):
    """
    读取目前所有规则，
    :return:
    """
    # 先判断发信息的这个群是否在规则里面，看是否在gm_rule_dict中
    # 如果没有则返回，没什么操作，同样的方法验证gm_rule_dict
    # 如果有，则依次进行匹配，一旦一个分类匹配到，立即停止该匹配，插入任务

    chatroomname = a_message.talker
    content = str_to_unicode(a_message.real_content)
    talker = a_message.real_talker

    if not talker:
        raise ValueError("没有message_said_username")

    if chatroomname not in gm_rule_dict:
        return False

    # 处理自动回复信息
    status_flag = False
    for matching_rule in gm_rule_dict[chatroomname]:
        for match_type, keywords_list in matching_rule.get("keywords").iteritems():
            if match_type == "precise" and content in keywords_list:
                reply_content_list = matching_rule.get("reply_content")
                status_flag = send_msg_to_android(a_message.bot_username, reply_content_list, [chatroomname])
                if status_flag == SUCCESS:
                    logger.info(u"精准匹配，自动回复任务发送成功, bot_username: %s." % a_message.bot_username)
                    break
                else:
                    logger.info(u"精准匹配，自动回复任务发送失败, bot_username: %s." % a_message.bot_username)
                    break
            if match_type == "fuzzy":
                for keyword in keywords_list:
                    if keyword in content and (u'@' + keyword) not in content:
                        reply_content_list = matching_rule.get("reply_content")
                        status_flag = send_msg_to_android(a_message.bot_username, reply_content_list, [chatroomname])
                        if status_flag == SUCCESS:
                            logger.info(u"模糊匹配，自动回复任务发送成功, bot_username: %s." % a_message.bot_username)
                            break
                        else:
                            logger.info(u"模糊匹配，自动回复任务发送失败, bot_username: %s." % a_message.bot_username)
                            break

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

    _gm_default_rule_dict = {}
    _gm_default_rule_dict.setdefault("is_full_match", {})
    _gm_default_rule_dict.setdefault("is_not_full_match", {})

    # 目前先用主表来判断
    coin_list = BaseModel.fetch_all(Coin, "*", where_clause = {"is_integral": 1})
    for coin in coin_list:
        if coin.symbol in ["OK", "YES"]:
            continue
        if coin.symbol:
            _gm_default_rule_dict["is_full_match"].setdefault(coin.symbol, coin.coin_id)
        if coin.coin_name_cn:
            _gm_default_rule_dict["is_full_match"].setdefault(coin.coin_name_cn, coin.coin_id)
    #
    # qr_quotes_dkr_info_list = db.session.query(RealTimeQuotesDefaultKeywordRelateInfo).all()
    # for qr_quotes_dkr_info in qr_quotes_dkr_info_list:
    #     if qr_quotes_dkr_info.is_full_match:
    #         gm_default_rule_dict["is_full_match"].setdefault(qr_quotes_dkr_info.keyword, qr_quotes_dkr_info.ds_id)
    #     else:
    #         gm_default_rule_dict["is_not_full_match"].setdefault(qr_quotes_dkr_info.keyword, qr_quotes_dkr_info.ds_id)
    return _gm_default_rule_dict


gm_rule_dict = get_gm_rule_dict()
gm_default_rule_dict = get_gm_default_rule_dict()
