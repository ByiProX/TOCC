# -*- coding: utf-8 -*-
from datetime import datetime

from configs.config import db, SUCCESS
from models.android_db_models import ABot
# from models.material_library_models import MaterialLibraryDefault
# from models.real_time_quotes_models import RealTimeQuotesDefaultSettingInfo, RealTimeQuotesDefaultKeywordRelateInfo, \
#     RealTimeQuotesDefaultMaterialRelate
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


class SetRealTimeQuoteSettingByManual:
    def __init__(self):
        pass

    @staticmethod
    def set_a_coin_setting_just_one_text(keyword_list, one_text):
        """
        老版代码，现在数据库格式已经更改
        """
        raise NotImplementedError
        # now_time = datetime.now()
        # rt_quotes_ds_info = RealTimeQuotesDefaultSettingInfo()
        # rt_quotes_ds_info.create_time = now_time
        # db.session.add(rt_quotes_ds_info)
        # db.session.commit()
        #
        # ds_id = rt_quotes_ds_info.ds_id
        #
        # # 存入关键词
        # for i, keyword in enumerate(keyword_list):
        #     rt_quotes_dkr_info = RealTimeQuotesDefaultKeywordRelateInfo()
        #     rt_quotes_dkr_info.ds_id = ds_id
        #     rt_quotes_dkr_info.keyword = keyword
        #     rt_quotes_dkr_info.is_full_match = True
        #     rt_quotes_dkr_info.send_seq = i
        #     db.session.add(rt_quotes_dkr_info)
        # db.session.commit()
        #
        # # 新建默认模板
        # mld_info = MaterialLibraryDefault()
        # # 文字类型
        # mld_info.task_send_type = 1
        # mld_info.task_send_content = {"text": one_text}
        # mld_info.used_count = 0
        # mld_info.create_time = now_time
        # mld_info.last_used_time = now_time
        # db.session.add(mld_info)
        # db.session.commit()
        #
        # dm_id = mld_info.dm_id
        #
        # # 存入物料关系
        # rt_quotes_ds_ml_rel = RealTimeQuotesDefaultMaterialRelate()
        # rt_quotes_ds_ml_rel.ds_id = ds_id
        # rt_quotes_ds_ml_rel.dm_id = dm_id
        # rt_quotes_ds_ml_rel.send_seq = 0
        # db.session.add(rt_quotes_ds_ml_rel)
        # db.session.commit()
