# -*- coding: utf-8 -*-

from configs.config import db


class UserAutoReplyRule(db.Model):
    """
    每个用户的自动回复的规则
    """
    pass


class CommonAutoReplyRule(db.Model):
    """
    全局的自动回复的规则
    """
    pass


class AutoReplyStream(db.Model):
    """
    所有识别到的reply的任务流
    """
    pass
