# -*- coding: utf-8 -*-

# IDE问题，import time无报错
import time
import threading
import logging

from datetime import datetime, timedelta
from sqlalchemy import desc

from configs.config import PRODUCTION_CIRCLE_INTERVAL, db, GLOBAL_MATCHING_RULES_UPDATE_FLAG
from core.matching_rule_core import get_gm_rule_dict, match_message_by_rule
from core.message_core import analysis_and_save_a_message
from core.qun_manage_core import check_whether_message_is_add_qun, check_is_removed
from core.user_core import check_whether_message_is_add_friend
from models.android_db_models import AMessage
from models.matching_rule_models import GlobalMatchingRule
from models.production_consumption_models import ProductionStatistic

logger = logging.getLogger('main')


class ProductionThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True
        self.run_start_time = None
        self.run_end_time = None
        self.last_a_message_id = None
        self.last_a_message_create_time = None

    def run(self):
        global GLOBAL_MATCHING_RULES_UPDATE_FLAG
        logger.info(u"Start thread id: %s." % str(self.thread_id))
        self.run_start_time = datetime.now()

        # 从这里要去库中读取上次循环的结果
        pro_stat = db.session.query(ProductionStatistic).order_by(desc(ProductionStatistic.sid)).first()
        if pro_stat:
            self.last_a_message_id = pro_stat.last_a_message_id
            self.last_a_message_create_time = pro_stat.last_a_message_create_time
        # 从来没有转起来过的时候的处理方法
        else:
            first_a_message = db.session.query(AMessage).order_by(AMessage.id).first()
            if first_a_message:
                self.last_a_message_id = first_a_message.id
                self.last_a_message_create_time = first_a_message.create_time
            else:
                self.last_a_message_id = 0
                self.last_a_message_create_time = datetime.now() - timedelta(days=365 * 10)

        gm_rule_dict = get_gm_rule_dict()
        GLOBAL_MATCHING_RULES_UPDATE_FLAG = False
        while self.go_work:
            circle_start_time = time.time()
            message_list = db.session.query(AMessage). \
                filter(AMessage.id > self.last_a_message_id). \
                order_by(AMessage.id).all()

            # 每次循环时，如果全局锁发生变更，则重新读取规则
            if GLOBAL_MATCHING_RULES_UPDATE_FLAG:
                gm_rule_dict = get_gm_rule_dict()
                GLOBAL_MATCHING_RULES_UPDATE_FLAG = False

            message_analysis_list = list()
            if len(message_list) != 0:
                for i, a_message in enumerate(message_list):
                    message_analysis = analysis_and_save_a_message(a_message)
                    if not message_analysis:
                        continue
                    message_analysis_list.append(message_analysis)

                    # is_add_friend
                    is_add_friend = check_whether_message_is_add_friend(message_analysis)
                    if is_add_friend:
                        continue

                    # 检查信息是否为加了一个群
                    is_add_qun = check_whether_message_is_add_qun(message_analysis)
                    if is_add_qun:
                        continue

                    # is_removed
                    is_removed = check_is_removed(message_analysis)

                    # 根据规则和内容进行匹配，并生成任务
                    match_message_by_rule(gm_rule_dict, message_analysis)

                    # 处理完毕后将新情况存入

                self.last_a_message_id = message_list[-1].id
                self.last_a_message_create_time = message_list[-1].create_time
            else:
                pass

            # 更新循环情况
            for i, message_analysis in enumerate(message_analysis_list):
                db.session.add(message_analysis)

            new_pro_stat = ProductionStatistic()
            new_pro_stat.last_a_message_id = self.last_a_message_id
            new_pro_stat.last_a_message_create_time = self.last_a_message_create_time
            new_pro_stat.create_time = datetime.now()
            db.session.add(new_pro_stat)
            db.session.commit()

            circle_now_time = time.time()
            time_to_rest = PRODUCTION_CIRCLE_INTERVAL - (circle_now_time - circle_start_time)
            if time_to_rest > 0:
                time.sleep(time_to_rest)
            else:
                pass
        logger.info(u"End thread id: %s." % str(self.thread_id))
        self.run_end_time = datetime.now()

    def stop(self):
        logger.info(u"停止进程")
        self.go_work = False


production_thread = ProductionThread(thread_id='pcwiyQgeoilnoBkS')
