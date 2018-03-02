# -*- coding: utf-8 -*-
import json
import logging

from datetime import datetime

from sqlalchemy import func

from configs.config import ERR_WRONG_FUNC_STATUS, db, SUCCESS, ERR_WRONG_ITEM, CONSUMPTION_TASK_TYPE, TASK_SEND_TYPE, \
    ERR_WRONG_USER_ITEM, GLOBAL_RULES_UPDATE_FLAG, GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG
from models.android_db_models import AContact
from models.production_consumption_models import ConsumptionTask
from models.qun_friend_models import UserQunRelateInfo, UserQunBotRelateInfo
from models.real_time_quotes_models import RealTimeQuotesDSUserRelate, RealTimeQuotesDefaultSettingInfo
from models.user_bot_models import UserBotRelateInfo, BotInfo
from utils.u_transformat import str_to_unicode, decimal_to_str

logger = logging.getLogger('main')


def switch_func_real_time_quotes(user_info, switch):
    """
    打开或关闭实时报价功能
    :param user_info:
    :param switch:
    :return:
    """
    if user_info.func_real_time_quotes and switch:
        logger.error("目前已为开启状态，无需再次开启. 返回正常.")
        return SUCCESS
    if not user_info.func_real_time_quotes and not switch:
        logger.error("目前已为关闭状态，无需再次开启. 返回正常.")
        return SUCCESS

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
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG] = True
    elif switch is False:
        rt_quotes_dsu_rel_list = db.session.query(RealTimeQuotesDSUserRelate).filter(
            RealTimeQuotesDSUserRelate.user_id == user_info.user_id).all()

        for rt_quotes_dsu_rel in rt_quotes_dsu_rel_list:
            db.session.delete(rt_quotes_dsu_rel)

        user_info.func_real_time_quotes = False
        db.session.commit()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG] = True

    return SUCCESS


def get_rt_quotes_list_and_status(user_info, per_page, page_number):
    # FIXME 此处应按照个人读取，而不应该所有人读取相同的结果
    # 因为目前进度比较急，所以直接读取全部人的结果
    ds_info_list = db.session.query(RealTimeQuotesDefaultSettingInfo).order_by(
        RealTimeQuotesDefaultSettingInfo.ds_id).limit(per_page).offset(page_number).all()

    ds_info_count = db.session.query(func.count(RealTimeQuotesDefaultSettingInfo)).first()
    if ds_info_count:
        count = int(ds_info_count[0])
    else:
        count = 0

    res = []
    for ds_info in ds_info_list:
        res_dict = {}
        res_dict.setdefault("coin_id", ds_info.ds_id)
        res_dict.setdefault("coin_name", ds_info.coin_name)
        res_dict.setdefault("logo", ds_info.coin_icon)
        res.append(res_dict)
    return SUCCESS, res, user_info.func_real_time_quotes, count


def get_rt_quotes_preview(coin_id):
    ds_info = db.session.query(RealTimeQuotesDefaultSettingInfo).filter(
        RealTimeQuotesDefaultSettingInfo.ds_id == coin_id).first()
    if not ds_info:
        logger.error(u"没有对应的币号. coin_id: %s." % coin_id)
        return ERR_WRONG_ITEM, None

    res = {}
    res.setdefault("coin_id", coin_id)
    res.setdefault("name", ds_info.coin_name)
    res.setdefault("logo", ds_info.coin_icon)
    res.setdefault("price", ds_info.price.to_eng_string())
    res.setdefault("all_price", ds_info.marketcap.to_eng_string())
    res.setdefault("rank", ds_info.rank)
    res.setdefault("coin_num", ds_info.available_supply.to_eng_string())
    res.setdefault("add_rate", ds_info.change1d.to_eng_string())
    res.setdefault("change_num", ds_info.volume_ex.to_eng_string())
    res.setdefault("keyword_list", [])

    # # 目前先用主表来存储关键词
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
    #     RealTimeQuotesDefaultKeywordRelateInfo.ds_id == coin_id).all()
    #
    # for ds_keyword_info in ds_keyword_list:
    #     res["keyword_list"].append(ds_keyword_info.keyword)

    return SUCCESS, res


def match_message_by_coin_keyword(gm_default_rule_dict, message_analysis):
    is_match_coin_keyword = False
    message_chatroomname = message_analysis.talker
    message_text = str_to_unicode(message_analysis.real_content)
    message_text = message_text.upper()
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
    ds_info = db.session.query(RealTimeQuotesDefaultSettingInfo).filter(
        RealTimeQuotesDefaultSettingInfo.ds_id == ds_id).first()
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

            a_contact = db.session.query(AContact).filter(AContact.username == message_said_username).first()
            if not a_contact:
                logger.error(u"无法找到该人名称")
                nickname = u""
            else:
                nickname = str_to_unicode(a_contact.nickname)
            res_text = u"@" + nickname + u" \n"

            # 计算价格
            price = decimal_to_str(ds_info.price)
            if "." in price:
                p_split = price.split(".")
                if len(p_split[1]) > 4:
                    price = p_split[0] + "." + p_split[1][:4]

            res_text += ds_info.coin_name + u"的价格为：$" + price + u"\n"

            res_text += u"当前市值：$" + decimal_to_str(ds_info.marketcap) + u"\n"

            res_text += u"流通数量：" + decimal_to_str(ds_info.available_supply) + u"\n"

            res_text += u"推荐交易所：\n"
            if ds_info.suggest_ex1:
                res_text += ds_info.suggest_ex1 + u" " + ds_info.suggest_ex1_url + "\n"
            if ds_info.suggest_ex2:
                res_text += ds_info.suggest_ex2 + u" " + ds_info.suggest_ex2_url + "\n"
            # if ds_info.suggest_ex1:
            #     res_text += u'推荐交易所：<a href="' + ds_info.suggest_ex1_url + u'">' + ds_info.suggest_ex1 + u'</a>\n'
            # if ds_info.suggest_ex2:
            #     res_text += u'<a href="' + ds_info.suggest_ex2_url + u'">' + ds_info.suggest_ex2 + u'</a>\n'

            # 24小时涨幅计算
            hour24changed = decimal_to_str(ds_info.change1d)
            if hour24changed[0] != "-":
                hour24changed = "+" + hour24changed
            res_text += u"24小时涨幅：" + hour24changed + u"%\n"

            res_text += unicode(ds_info.create_time)[:19] + u"\n"
            res_text += u"【友问币答 来源" + u"block.cc】"

            c_task.task_send_content = json.dumps({"text": res_text})

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
