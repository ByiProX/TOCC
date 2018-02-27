# -*- coding: utf-8 -*-

import logging

from configs.config import ERR_WRONG_FUNC_STATUS, db, CONSUMPTION_TASK_TYPE, GLOBAL_MATCHING_RULES_UPDATE_FLAG, SUCCESS
from models.matching_rule_models import GlobalMatchingRule
from models.real_time_quotes_models import RealTimeQuotesDSUserRelate

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

    switch_choose = [True, False]
    for choose in switch_choose:
        if switch == choose:
            rt_quotes_dsu_rel_list = db.session.query(RealTimeQuotesDSUserRelate).filter(
                RealTimeQuotesDSUserRelate.user_id == user_info.user_id).all()

            for rt_quotes_dsu_rel in rt_quotes_dsu_rel_list:
                db.session.delete(rt_quotes_dsu_rel)
            db.session.commit()

            gm_rule_list = db.session.query(GlobalMatchingRule).filter(
                GlobalMatchingRule.user_id == user_info.user_id,
                GlobalMatchingRule.task_type == CONSUMPTION_TASK_TYPE['real_time_quotes']).all()
            for gm_rule in gm_rule_list:
                gm_rule.is_take_effect = choose
                db.session.merge(gm_rule)

            user_info.func_auto_reply = choose
            db.session.merge(user_info)
            db.session.commit()
            GLOBAL_MATCHING_RULES_UPDATE_FLAG["global_matching_rules_update_flag"] = True

    return SUCCESS
