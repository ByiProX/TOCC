# -*- coding: utf-8 -*-
from datetime import datetime

from configs.config import db, SUCCESS
from models.android_db_models import ABot
from models.user_bot_models import BotInfo


class SetBotRelSettingByManual:
    def __init__(self):
        pass

    @staticmethod
    def set_bot_info_by_a_bot_db():
        """
        当已经有新bot在ABot表中时，将BotInfo于ABot同步
        :return:
        """
        a_bot_list = db.session.query(ABot).all()
        bot_info_list = db.session.query(BotInfo).all()

        exist_bot_username_list = []
        for bot_info_iter in bot_info_list:
            exist_bot_username_list.append(bot_info_iter.username)

        for a_bot_iter in a_bot_list:
            if a_bot_iter.username in exist_bot_username_list:
                continue
            else:
                new_bot_info = BotInfo()
                new_bot_info.username = a_bot_iter.username
                new_bot_info.create_bot_time = datetime.now()
                new_bot_info.is_alive = True
                new_bot_info.alive_detect_time = datetime.now()
                db.session.add(new_bot_info)
                db.session.commit()
        return SUCCESS
