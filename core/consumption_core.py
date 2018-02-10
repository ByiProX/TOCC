# -*- coding: utf-8 -*-

# IDE问题，import time无报错
import json
import random

import time
import threading
import logging

from datetime import datetime

from configs.config import db, CONSUMPTION_CIRCLE_INTERVAL
from core.send_task_and_ws_setting_core import send_task_content_to_ws
from models.production_consumption_models import ConsumptionTask, ConsumptionStatistic, \
    ConsumptionTaskStream
from models.user_bot_models import BotInfo

logger = logging.getLogger('main')

SEND_FREQUENCY_LIMITATION_DICT = dict()


class ConsumptionThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True
        self.run_start_time = None
        self.run_end_time = None

        self.bot_username = self.thread_id[15:]
        bot_info = db.session.query(BotInfo).filter(BotInfo.username == self.bot_username).first()
        if not bot_info:
            raise ValueError("没有该bot，无法启动")

    def run(self):
        logger.info(u"Start thread id: %s." % str(self.thread_id))
        self.run_start_time = datetime.now()

        while self.go_work:
            circle_start_time = time.time()

            ct_list = db.session.query(ConsumptionTask).filter(ConsumptionTask.bot_username == self.bot_username). \
                order_by(ConsumptionTask.task_id).all()

            for i, each_task in enumerate(ct_list):
                if each_task.task_type == 1:
                    task_send_content = json.loads(each_task.task_send_content)
                    send_task_content_to_ws(each_task.bot_username, each_task.chatroomname,
                                            each_task.task_send_type, task_send_content['text'])
                    time.sleep(random.random() + 0.6)
                else:
                    logger.warning("目前不进行处理")

                c_task_s = ConsumptionTaskStream()
                c_task_s.task_id = each_task.task_id
                c_task_s.qun_owner_user_id = each_task.qun_owner_user_id
                c_task_s.task_initiate_user_id = each_task.task_initiate_user_id
                c_task_s.chatroomname = each_task.chatroomname
                c_task_s.task_type = each_task.task_type
                c_task_s.task_relevant_id = each_task.task_relevant_id
                c_task_s.task_send_type = each_task.task_send_type
                c_task_s.task_send_content = each_task.task_send_content
                c_task_s.bot_username = each_task.bot_username
                c_task_s.message_received_time = each_task.message_received_time
                c_task_s.task_create_time = each_task.task_create_time
                c_task_s.send_to_ws_time = datetime.now()
                c_task_s.task_status = 0
                db.session.add(c_task_s)
                db.session.delete(ct_list[i])

            new_con_stat = ConsumptionStatistic()
            new_con_stat.ct_count = len(ct_list)
            new_con_stat.create_time = datetime.now()
            db.session.add(new_con_stat)
            db.session.commit()

            circle_now_time = time.time()
            time_to_rest = CONSUMPTION_CIRCLE_INTERVAL - (circle_now_time - circle_start_time)
            if time_to_rest > 0:
                time.sleep(time_to_rest)
            else:
                pass
        logger.info(u"End thread id: %s." % str(self.thread_id))
        self.run_end_time = datetime.now()

    def stop(self):
        logger.info(u"停止进程")
        self.go_work = False

#
# class SendingTask(threading.Thread):
#     def __init__(self, thread_id, bot_username, target_username, task_send_type, content):
#         threading.Thread.__init__(self)
#         self.thread_id = thread_id
#
#         self.bot_username = bot_username
#         self.target_username = target_username
#         self.task_send_type = task_send_type
#         self.content = content
#
#     def run(self):
#         logger.info(u"发送数据线程: %s." % str(self.thread_id))
#         global SEND_FREQUENCY_LIMITATION_DICT
#         SEND_FREQUENCY_LIMITATION_DICT.setdefault(self.bot_username, [])
#
#         while True:
#             status = self.check_whether_can_send()
#             if status is True:
#                 break
#             else:
#                 time.sleep(random.random() + 0.4)
#
#         send_task_content_to_ws(self.bot_username, self.target_username, self.task_send_type, self.content)
#         logger.info(u"发送完成！: %s." % str(self.thread_id))
#
#     def check_whether_can_send(self):
#         global SEND_FREQUENCY_LIMITATION_DICT
#         now_datetime = datetime.now()
#         if not SEND_FREQUENCY_LIMITATION_DICT[self.bot_username]:
#             return True
#         if SEND_FREQUENCY_LIMITATION_DICT[self.bot_username][-1] < now_datetime - timedelta(microseconds=200):
#             return False
#         for each_iter in range(len(SEND_FREQUENCY_LIMITATION_DICT[self.bot_username]) - 1, -1, -1):
#             if SEND_FREQUENCY_LIMITATION_DICT[self.bot_username][each_iter] < now_datetime - timedelta(seconds=5):
#                 SEND_FREQUENCY_LIMITATION_DICT[self.bot_username].pop(each_iter)
#             else:
#                 pass
#         if len(SEND_FREQUENCY_LIMITATION_DICT[self.bot_username]) < 5:
#             return True
#         else:
#             return False
