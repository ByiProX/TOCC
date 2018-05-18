# -*- coding: utf-8 -*-
import threading
import logging
import time
from models_v2.base_model import BaseModel
from configs.config import TIMED_BATCH_SENDING_INTERVAL, BATCH_SEND_TASK_STATUS_3, BATCH_SEND_TASK_STATUS_4
from core_v2.send_msg import send_msg_to_android
from configs.config import SUCCESS, UserBotR

logger = logging.getLogger('main')


class VipCheckThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True

    def run(self):
        logger.info(u"Start thread id: %s." % str(self.thread_id))
        while self.go_work:
            not_vip_list = BaseModel.fetch_all("client_qun_r", "*",
                                               where_clause=BaseModel.and_(
                                                   ["=", "is_vip", 0],
                                                   # [">", "create_time", cur_time - 30 * 60],
                                                   [">", "qun_used_count", 1]),
                                               order_by=BaseModel.order_by({"create_time": "ASC"})
                                               )

            for not_vip in not_vip_list:
                sleep_time = 30 * 60 - (not_vip.create_time - int(time.time())) \
                    if 30 * 60 - (not_vip.create_time - int(time.time())) > 0 else 0
                time.sleep(sleep_time)
                

            # print tasks
            while True:
                try:
                    task = tasks.pop(0)
                    cur_time = int(time.time())
                    send_time = task.send_time
                    time.sleep(send_time - cur_time)

                    # 传给安卓发送
                    # batch_send_task = CM(BatchSendTask)
                    ubr = BaseModel.fetch_one(UserBotR, '*',
                                              where_clause=BaseModel.where_dict({"client_id": task.client_id}))

                    status = send_msg_to_android(ubr.bot_username, task.content_list, task.chatroom_list)
                    task.send_time_real = int(time.time())
                    if status == SUCCESS:
                        logger.info(u"任务发送成功, client_id: %s." % task.client_id)
                        task.status = BATCH_SEND_TASK_STATUS_3
                        task.save()
                    else:
                        logger.info(u"任务发送失败, client_id: %s." % task.client_id)
                        task.status = BATCH_SEND_TASK_STATUS_4
                        task.save()
                except IndexError:
                    break
            # end_time = int(time.time())
            # time.sleep(TIMED_BATCH_SENDING_INTERVAL - (end_time - start_time))
            # time.sleep(5)

    def stop(self):
        logger.info(u"停止进程")
        self.go_work = False


vip_check_task_thread = VipCheckThread(thread_id='vip checkout task')
