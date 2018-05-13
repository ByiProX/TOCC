# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from configs.config import db, ERR_WRONG_ITEM
from models.production_consumption_models import ConsumptionTaskStream
from models.user_bot_models import BotInfo

LIMITATION_OF_FIVE_SECONDS = 2
# LIMITATION_OF_TEN_SECONDS = 4
# LIMITATION_OF_HALF_MINUTES = 12
# LIMITATION_OF_ONE_MINUTES = 24
# LIMITATION_OF_FIVE_MINUTES = 120
# LIMITATION_OF_TEN_MINUTES = 240
# LIMITATION_OF_HALF_HOURS = 720
LIMITATION_OF_ONE_HOURS = 1440


def check_bot_sending_capability(bot_info=None, bot_id=None):
    if not bot_info and not bot_id:
        raise ValueError("传入参数有误")

    if bot_id:
        bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == bot_id).first()

    if not bot_info:
        return ERR_WRONG_ITEM

    now_datetime = datetime.now()
    last_one_hours_datetime = now_datetime - timedelta(hours=1)
    c_task_list = db.session.query(ConsumptionTaskStream).filter(ConsumptionTaskStream.send_to_ws_time).all()
    if len(c_task_list) > LIMITATION_OF_ONE_HOURS:
        return False

    # 这个部分先不处理
    # 原本准备每次都请求一下，但是读库操作太大，所以现在变成把控制放在循环中
    # 这个循环比较难写，所以先不写
    raise NotImplementedError
