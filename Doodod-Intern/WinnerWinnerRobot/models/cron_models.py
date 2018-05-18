from datetime import datetime

from configs.config import db


class CronLog(db.Model):
    __tablename__ = 'cron_log'
    cron_type = db.Column(db.Integer, primary_key = True)
    create_time = db.Column(db.DateTime, primary_key = True)

    def __init__(self, cron_type):
        self.cron_type = cron_type
        self.create_time = datetime.now()
