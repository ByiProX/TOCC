# -*- coding: utf-8 -*-
from sqlalchemy import desc

from configs.config import db
from models.matching_rule_models import GlobalMatchingRule, MatchingRuleInMemory


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
        gm_rule_dict[gm_rule.chatroomname].setdefault(gm_rule.task_type)

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

def _add_task_to_consumption_task():
    """
    确认生成任务后，调用该函数进行任务生成
    :return:
    """
    # 因为前端设置和调用均没有确定，所以暂时无法写这部分