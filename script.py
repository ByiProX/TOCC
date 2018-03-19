# -*- coding: utf-8 -*-
from configs.config import db
from core.message_core import analysis_and_save_a_message
from models.android_db_models import AMessage
from models.message_ext_models import MessageAnalysis
from models.production_consumption_models import ProductionStatistic

pro_stat = db.session.query(ProductionStatistic).order_by(ProductionStatistic.sid.desc()).first()
a_msg_list = db.session.query(AMessage).filter(AMessage.create_time < pro_stat.last_a_message_create_time,
                                               AMessage.id >= 28000).all()

for a_msg in a_msg_list:
    print a_msg.id
    message_analysis = analysis_and_save_a_message(a_msg)
    db.session.merge(message_analysis)

db.session.commit()

pass
