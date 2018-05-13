# -*- coding: utf-8 -*-
import json
import logging

from datetime import datetime

from sqlalchemy import func

from configs.config import db, SUCCESS, ERR_WRONG_ITEM, CONSUMPTION_TASK_TYPE, TASK_SEND_TYPE, \
    ERR_WRONG_USER_ITEM, UserSwitch, Coin, MSG_TYPE_TXT
from core_v2.send_msg import send_msg_to_android
from models_v2.base_model import BaseModel
from utils.u_transformat import str_to_unicode, trim_str

logger = logging.getLogger('main')


def switch_func_real_time_quotes(user_info, switch):
    """
    打开或关闭实时报价功能
    :param user_info:
    :param switch:
    :return:
    """
    user_switch = BaseModel.fetch_one(UserSwitch, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    if user_switch is None:
        logger.error("没有找到该用户的开关配置.")
        return ERR_WRONG_ITEM

    user_switch.func_real_time_quotes = 1 if switch else 0
    user_switch.save()

    return SUCCESS


def get_rt_quotes_list_and_status(user_info, per_page, page_number):
    # FIXME 此处应按照个人读取，而不应该所有人读取相同的结果
    # 因为目前进度比较急，所以直接读取全部人的结果
    ds_info_list = BaseModel.fetch_all(Coin, ["coin_id", "coin_name", "coin_icon"], where_clause = BaseModel.where_dict({"is_integral": 1}), order_by = BaseModel.order_by({"marketcap": "desc"}), page = page_number, pagesize = per_page)

    ds_info_count = BaseModel.count(Coin, where_clause = BaseModel.where_dict({"is_integral": 1}))

    res = []
    for ds_info in ds_info_list:
        res_dict = {}
        res_dict.setdefault("coin_id", ds_info.coin_id)
        res_dict.setdefault("coin_name", ds_info.coin_name)
        res_dict.setdefault("logo", ds_info.coin_icon)
        res.append(res_dict)
    user_switch = BaseModel.fetch_one(UserSwitch, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    return SUCCESS, res, user_switch.func_real_time_quotes, ds_info_count


def get_rt_quotes_preview(coin_id):
    # ds_info = BaseModel.fetch_one(Coin, "*", where_clause = BaseModel.where_dict({"is_integral": 1, "coin_id": coin_id}))
    ds_info = BaseModel.fetch_by_id(Coin, coin_id)
    if not ds_info:
        logger.error(u"没有对应的币号. coin_id: %s." % coin_id)
        return ERR_WRONG_ITEM, None

    res = {}
    res.setdefault("coin_id", coin_id)
    res.setdefault("name", ds_info.coin_name)
    res.setdefault("logo", ds_info.coin_icon)

    # 组合后的结果
    # text = _build_a_rs_text_to_send(message_said_username=None, ds_info=ds_info)
    # res.setdefault("text", text)
    # res.setdefault("price", ds_info.price.to_eng_string())
    # res.setdefault("all_price", ds_info.marketcap.to_eng_string())
    # res.setdefault("rank", ds_info.rank)
    # res.setdefault("coin_num", ds_info.available_supply.to_eng_string())
    # res.setdefault("add_rate", ds_info.change1d.to_eng_string())
    # res.setdefault("change_num", ds_info.volume_ex.to_eng_string())
    # res.setdefault("keyword_list", [])
    text = _build_a_rs_text_to_send(message_said_username=None, coin =ds_info)
    res.setdefault("text", text)
    res.setdefault("price", ds_info.price)
    res.setdefault("all_price", ds_info.marketcap)
    res.setdefault("rank", ds_info.rank)
    res.setdefault("coin_num", ds_info.available_supply)
    res.setdefault("add_rate", ds_info.change1d)
    res.setdefault("change_num", ds_info.volume_ex)
    res.setdefault("keyword_list", [])

    # 目前先用主表来存储关键词
    if ds_info.symbol:
        res['keyword_list'].append(ds_info.symbol)
    else:
        pass

    if ds_info.coin_name_cn:
        res['keyword_list'].append(ds_info.coin_name_cn)
    else:
        pass
    #
    # ds_keyword_list = db.session.query(RealTimeQuotesDefaultKeywordRelateInfo).filter(
    #     RealTimeQuotesDefaultKeywordRelateInfo.coin_id == coin_id).all()
    #
    # for ds_keyword_info in ds_keyword_list:
    #     res["keyword_list"].append(ds_keyword_info.keyword)

    return SUCCESS, res


def match_message_by_coin_keyword(gm_default_rule_dict, a_message):
    is_match_coin_keyword = False
    if a_message.is_to_friend:
        return is_match_coin_keyword

    message_chatroomname = a_message.talker
    message_text = str_to_unicode(a_message.real_content)
    message_text = message_text.upper()
    message_said_username = a_message.real_talker
    bot_username = a_message.bot_username

    if not message_said_username:
        raise ValueError("没有message_said_username")

    if message_text in gm_default_rule_dict['is_full_match']:
        # 已经匹配到了text，执行后续操作
        logger.info(u"匹配到币种信息. symbol: %s." % message_text)
        coin = BaseModel.fetch_one(Coin, "*", where_clause = BaseModel.where_dict({"symbol": message_text}))
        content = _build_a_rs_text_to_send(message_said_username, coin)
        message_json = dict()
        message_json["type"] = MSG_TYPE_TXT
        message_json["content"] = content
        message_json["seq"] = 0
        message_list = [message_json]
        to_list = [message_chatroomname]
        send_msg_to_android(bot_username, message_list, to_list)
        # activate_rule_and_add_task_to_consumption_task(gm_default_rule_dict['is_full_match'][message_text],
        #                                                message_chatroomname, message_said_username)
        is_match_coin_keyword = True
        pass

    for keyword, coin_id in gm_default_rule_dict['is_not_full_match']:
        if keyword in message_text:
            logger.info(u"匹配到币种信息. symbol: %s." % message_text)
            coin = BaseModel.fetch_one(Coin, "*", where_clause = BaseModel.where_dict({"symbol": message_text}))
            content = _build_a_rs_text_to_send(message_said_username, coin)
            message_json = dict()
            message_json["type"] = MSG_TYPE_TXT
            message_json["content"] = content
            message_json["seq"] = 0
            message_list = [message_json]
            to_list = [message_chatroomname]
            send_msg_to_android(bot_username, message_list, to_list)
            # activate_rule_and_add_task_to_consumption_task(gm_default_rule_dict['is_not_full_match'][message_text],
            #                                                message_chatroomname, message_said_username)
            is_match_coin_keyword = True

    return is_match_coin_keyword


# def activate_rule_and_add_task_to_consumption_task(coin_id, message_chatroomname, message_said_username):
#     ds_info = db.session.query(Coin).filter(
#         Coin.coin_id == coin_id,
#         Coin.is_integral == 1).first()
#     if not ds_info:
#         return ERR_WRONG_ITEM
#
#     uqr_info_list = db.session.query(UserQunRelateInfo).filter(
#         UserQunRelateInfo.chatroomname == message_chatroomname,
#         UserQunRelateInfo.is_deleted == 0).all()
#     if not uqr_info_list:
#         logger.warning("在未开启实时报价的群中发现报价关键字")
#         return ERR_WRONG_ITEM
#     chatroom_relate_user_id_dict = {}
#     for uqr_info in uqr_info_list:
#         chatroom_relate_user_id_dict.setdefault(uqr_info.user_id, uqr_info)
#
#     user_info_list = db.session.query(UserInfo).filter(UserInfo.func_real_time_quotes == 1).all()
#
#     for user_info in user_info_list:
#         if user_info.user_id in chatroom_relate_user_id_dict:
#             c_task = ConsumptionTask()
#             c_task.qun_owner_user_id = user_info.user_id
#             c_task.task_initiate_user_id = user_info.user_id
#
#             c_task.chatroomname = chatroom_relate_user_id_dict[user_info.user_id].chatroomname
#             c_task.task_type = CONSUMPTION_TASK_TYPE['real_time_quotes']
#             c_task.task_relevant_id = coin_id
#
#             c_task.task_send_type = TASK_SEND_TYPE['text']
#
#             res_text = _build_a_rs_text_to_send(message_said_username, ds_info)
#
#             c_task.task_send_content = json.dumps({"text": res_text})
#
#             uqun_id = chatroom_relate_user_id_dict[user_info.user_id].uqun_id
#
#             uqbr_info_list = db.session.query(UserQunBotRelateInfo).filter(
#                 UserQunBotRelateInfo.uqun_id == uqun_id).all()
#             if not uqbr_info_list:
#                 logger.error(u"没有找到群与机器人绑定关系. qun_id: %s." % uqun_id)
#                 return ERR_WRONG_USER_ITEM
#             user_bot_rid_list = []
#             for uqbr_info in uqbr_info_list:
#                 if uqbr_info.is_error is True:
#                     continue
#                 else:
#                     user_bot_rid_list.append(uqbr_info.user_bot_rid)
#             # 目前只要读取到一个bot_id就好
#             bot_id = None
#             for user_bot_rid in user_bot_rid_list:
#                 ubr_info = db.session.query(UserBotRelateInfo).filter(
#                     UserBotRelateInfo.user_bot_rid == user_bot_rid).all()
#                 bot_id = ubr_info[0].bot_id
#                 if bot_id:
#                     break
#
#             bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == bot_id).first()
#             if not bot_info:
#                 logger.error(u"没有找到bot相关信息. bot_id: %s." % bot_id)
#                 return ERR_WRONG_ITEM
#
#             c_task.bot_username = bot_info.username
#             now_time = datetime.now()
#             c_task.message_received_time = now_time
#             c_task.task_create_time = now_time
#
#             db.session.add(c_task)
#             db.session.commit()
#             return SUCCESS


def _build_a_rs_text_to_send(message_said_username, coin):
    res_text = u"\ud83d\udca1" + coin.coin_name + u" " + coin.coin_name_cn + u" 实时行情\ud83d\udca1 \n"
    res_text += u"-------------------------------\n"

    # price = decimal_to_str(ds_info.price)
    price = trim_str(coin.price)
    if "." in price:
        p_split = price.split(".")
        if len(p_split[1]) > 4:
            price = p_split[0] + u"." + p_split[1][:4]
    res_text += u"价格：￥" + price + u"\n"

    # 市场排名
    rank = coin.rank
    res_text += u"排名：第 " + unicode(rank) + u" 名\n"

    # 市值计算
    # marketcap = decimal_to_str(ds_info.marketcap)
    marketcap = trim_str(coin.marketcap)
    if "." in marketcap:
        m_s = marketcap.split(".")
        if int(m_s[0]) > 1000000000:
            marketcap = m_s[0][:-8] + u"." + m_s[0][-8:-6] + u"亿"
        elif int(m_s[0]) > 100000:
            marketcap = m_s[0][:-4] + u"." + m_s[0][-4:-2] + u"万"
    res_text += u"市值：￥" + marketcap + u"\n"

    # 流通数量
    # available_supply = decimal_to_str(ds_info.available_supply)
    available_supply = trim_str(coin.available_supply)
    if "." in available_supply:
        m_s = available_supply.split(".")
        if int(m_s[0]) > 1000000000:
            available_supply = m_s[0][:-8] + u"." + m_s[0][-8:-6] + u"亿"
        elif int(m_s[0]) > 100000:
            available_supply = m_s[0][:-4] + u"." + m_s[0][-4:-2] + u"万"
    res_text += u"流通盘：" + available_supply + u"\n"

    # 24小时涨幅计算
    # hour24changed = decimal_to_str(ds_info.change1d)
    hour24changed = trim_str(coin.change1d)
    if hour24changed[0] != "-":
        hour24changed = "+" + hour24changed
    res_text += u"24小时涨幅：" + hour24changed + u"%\n"

    res_text += u"数据来源：" + u"coinmarketcap\n"
    res_text += u"【" + unicode(datetime.fromtimestamp(coin.create_time))[:19] + u"】\n"
    res_text += u"\ud83d\udcc8 友问币答 YACA_coin"
    return res_text
