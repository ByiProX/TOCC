# -*- coding: utf-8 -*-
from datetime import datetime

from configs.config import db


class CrawlerLog(db.Model):
    """
    每次扫描的情况记录在这里
    """
    __tablename__ = 'crawler_log'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer, index = True, nullable = False)

    create_time = db.Column(db.DateTime, index=True, nullable=False)

    def __init__(self, status):
        self.status = status

    def generate_create_time(self, create_time = None):
        if create_time is None:
            create_time = datetime.now()
        self.create_time = create_time
        return self
