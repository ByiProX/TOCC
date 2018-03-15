# -*- coding: utf-8 -*-

# IDE问题，import time无报错
import traceback

import time
import threading
import logging

from datetime import datetime, timedelta
from sqlalchemy import desc

from configs.config import PRODUCTION_CIRCLE_INTERVAL, db, MSG_TYPE_TXT, MSG_TYPE_SYS
from models.android_db_models import AMessage
from models.message_ext_models import MessageAnalysis
from models.production_consumption_models import ProductionStatistic
from sqlalchemy import orm as sql_orm

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

        while self.go_work:
            try:
                circle_start_time = time.time()
                message_list = db.session.query(AMessage). \
                    filter(AMessage.id > self.last_a_message_id). \
                    order_by(AMessage.id).all()

                message_analysis_list = list()
                if len(message_list) != 0:
                    ProductionThread._process_a_msg_list(message_list, message_analysis_list)

                    # 处理完毕后将新情况存入
                    self.last_a_message_id = message_list[-1].id
                    self.last_a_message_create_time = message_list[-1].create_time

                    # 更新循环情况
                    for i, message_analysis in enumerate(message_analysis_list):
                        db.session.add(message_analysis)
                else:
                    pass

                new_pro_stat = ProductionStatistic()
                new_pro_stat.last_a_message_id = self.last_a_message_id
                new_pro_stat.last_a_message_create_time = self.last_a_message_create_time
                new_pro_stat.create_time = datetime.now()
                db.session.add(new_pro_stat)
                db.session.commit()

                # for message_analysis in message_analysis_list:
                #     if not message_analysis.is_to_friend:
                #         msg_count_thread = threading.Thread(target = MessageAnalysis.count_msg, name = u'MsgCountThread',
                #                                             args = (message_analysis.msg_id,))
                #         msg_count_thread.setDaemon(True)
                #         msg_count_thread.start()

                circle_now_time = time.time()
                time_to_rest = PRODUCTION_CIRCLE_INTERVAL - (circle_now_time - circle_start_time)
                if time_to_rest > 0:
                    time.sleep(time_to_rest)
                else:
                    pass
            except sql_orm.exc.ObjectDeletedError:
                logger.critical("原a_message的id对应的条目不存在")
                logger.critical("暂时不对该问题进行处理")
                logger.critical(traceback.format_exc())
                self.go_work = False
                logger.critical("循环停止运行")
            except Exception:
                logger.critical("发生未知错误，捕获所有异常，待查")
                logger.critical(traceback.format_exc())
                self.go_work = False
                logger.critical("循环停止运行")
        logger.info(u"End thread id: %s." % str(self.thread_id))
        self.run_end_time = datetime.now()

    def stop(self):
        logger.info(u"停止进程")
        self.go_work = False

    @staticmethod
    def _process_a_msg_list(message_list, message_analysis_list = None):
        if message_analysis_list is None:
            message_analysis_list = list()
        for i, a_message in enumerate(message_list):
            message_analysis = MessageAnalysis.analysis_and_save_a_message(a_message)
            if not message_analysis:
                continue
            message_analysis_list.append(message_analysis)

            # 判断这个机器人说的话是否是文字或系统消息
            if message_analysis.type == MSG_TYPE_TXT or message_analysis.type == MSG_TYPE_SYS:
                pass
            else:
                continue

            # 这个机器人说的话
            # TODO 当有两个机器人的时候，这里不仅要判断是否是自己说的，还是要判断是否是其他机器人说的
            if message_analysis.is_send == 1:
                continue

            # is_add_friend
            is_add_friend = MessageAnalysis.check_whether_message_is_add_friend(message_analysis)
            if is_add_friend:
                continue

            # 检查信息是否为加了一个群
            is_add_qun = MessageAnalysis.check_whether_message_is_add_qun(message_analysis)
            if is_add_qun:
                continue

            # is_removed
            is_removed = MessageAnalysis.check_is_removed(message_analysis)
            if is_removed:
                continue

            # 检测是否是别人的进群提示
            # is_friend_into_qun = MessageAnalysis.check_whether_message_is_friend_into_qun(message_analysis)

        return message_analysis_list


production_thread = ProductionThread(thread_id='pcwiyQgeoilnoBkS')
