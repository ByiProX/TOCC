# -*- coding: utf-8 -*-s

from configs.config import main_api, CRON_TYPE_CHATROOM_OVERVIEW, db, CRON_TYPE_CHATROOM_STATISTIC, \
    CRON_TYPE_MEMBER_OVERVIEW
from core.cron_core import update_chatroom_overview, update_member_overview, update_chatroom_statistics
from models.cron_models import CronLog


@main_api.route('/cron/update_chatroom_overview', methods=['GET', 'POST'])
def cron_update_chatroom_overview():
    update_chatroom_overview()
    cron_log = CronLog(cron_type = CRON_TYPE_CHATROOM_OVERVIEW)
    db.session.add(cron_log)
    db.session.commit()
    return 'SUCCESS'


@main_api.route('/cron/update_chatroom_statistics', methods=['GET', 'POST'])
def cron_update_chatroom_overview():
    update_chatroom_statistics()
    cron_log = CronLog(cron_type = CRON_TYPE_CHATROOM_STATISTIC)
    db.session.add(cron_log)
    db.session.commit()
    return 'SUCCESS'


@main_api.route('/cron/update_member_overview', methods=['GET', 'POST'])
def cron_update_member_overview():
    update_member_overview()
    cron_log = CronLog(cron_type = CRON_TYPE_MEMBER_OVERVIEW)
    db.session.add(cron_log)
    db.session.commit()
    return 'SUCCESS'


pass
