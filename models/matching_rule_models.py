# -*- coding: utf-8 -*-

from configs.config import db


class GlobalMatchingRule(db.Model):
    """
    全局的匹配统一到这里，然后再从这里读出去
    """
    mid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 规则从属于哪个人
    user_id = db.Column(db.BigInteger, index=True, nullable=False)

    # 适用于哪个群
    chatroomname = db.Column(db.String(32), index=True, nullable=False)

    match_word = db.Column(db.String(1024), index=True, nullable=False)

    # 1为群发消息(无)；2为自动回复；3为回复签到；4为入群回复
    task_type = db.Column(db.Integer, index=True, nullable=False)
    task_relevant_id = db.Column(db.BigInteger, index=True, nullable=False)

    # 规则生成时间
    create_time = db.Column(db.DateTime, index=True, nullable=False)

    # 精确匹配是指话与词完全匹配；非精确匹配是指只要包含即可
    is_exact_match = db.Column(db.Boolean, index=True, nullable=False)

    # 是否有效，如果无效则不进行读取
    is_take_effect = db.Column(db.Boolean, index=True, nullable=False)


class MatchingRuleInMemory:
    def __init__(self, mid, user_id, chatroomname, match_word, task_type, task_relevant_id, create_time,
                 is_exact_match):
        self.mid = mid
        self.user_id = user_id
        self.chatroomname = chatroomname
        self.match_word = match_word
        self.task_type = task_type
        self.task_relevant_id = task_relevant_id
        self.create_time = create_time
        self.is_exact_match = is_exact_match
