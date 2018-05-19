# -*- coding: utf-8 -*-
__author__ = "Quentin"

import threading
import logging
import time
from models_v2.base_model import BaseModel
from configs.config import TIMED_BATCH_SENDING_INTERVAL, BATCH_SEND_TASK_STATUS_3, BATCH_SEND_TASK_STATUS_4
from core_v2.send_msg import send_ws_to_android
from configs.config import SUCCESS, UserBotR

logger = logging.getLogger('main')


class FreeQunCheckThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True

    def run(self):
        logger.info(u"Start thread id: %s." % str(self.thread_id))
        while self.go_work:
            free_clients = BaseModel.fetch_all("client", "*",
                                               where_clause=BaseModel.and_(
                                                   ["=", "qun_count", 1],
                                               ))

            free_clients_id = [free_client.client_id for free_client in free_clients]

            cur_time = int(time.time())
            # 查找免费用户的多余群(未付费群)，--- 半小时内
            not_paid_quns = self.check_not_paid_quns(free_clients_id, cur_time)

            if not not_paid_quns:
                time.sleep(60)
                continue

            # 通知付款
            self.inform_to_pay(not_paid_quns)

            # 等待
            time.sleep(120)
            # 重新查表，查找未缴费群
            not_paid_quns_again = self.check_not_paid_quns(free_clients_id, cur_time)

            self.kick_out(not_paid_quns_again)

    @staticmethod
    def check_not_paid_quns(free_clients_id, cur_time):
        not_paid_quns = BaseModel.fetch_all("client_qun_r", "*",
                                            where_clause=BaseModel.and_(
                                                ["in", "client_id", free_clients_id],
                                                ["=", "is_paid", 0],
                                                [">", "create_time", cur_time - 28 * 60],
                                                ["<", "create_time", cur_time - 25 * 60]),
                                            order_by=BaseModel.order_by({"create_time": "ASC"})
                                            )

        return not_paid_quns

    @staticmethod
    def inform_to_pay(quns):
        for qun in quns:
            ubr = BaseModel.fetch_one(UserBotR, '*',
                                      where_clause=BaseModel.where_dict({"client_id": qun.client_id}))

            data = {
                "task": "send_message",
                "to": "%s" % qun.client_id,
                "type": 1,
                "content": "%s 尚未缴费, 请及时付款，否则2分钟后该群服务消失" % qun.chatroomname
            }
            try:
                status = send_ws_to_android(ubr.bot_username, data)
            except Exception:
                continue
            if status == SUCCESS:
                logger.info(u"任务发送成功, client_id: %s." % qun.client_id)
            else:
                logger.info(u"任务发送失败, client_id: %s." % qun.client_id)
        # return int(time.time())

    @staticmethod
    def kick_out(quns):
        for qun in quns:
            ubr = BaseModel.fetch_one(UserBotR, '*',
                                      where_clause=BaseModel.where_dict({"client_id": qun.client_id}))
            # TODO 退群接口添加
            data = {
                "task": "退群接口",
                "to": "%s" % qun.client_id,
                "type": 1,
                "content": "%s 已退群" % qun.chatroomname
            }
            sleep_time = 30 * 60 - (int(time.time()) - qun.create_time) \
                if 30 * 60 - (int(time.time()) - qun.create_time) > 0 else 0
            time.sleep(sleep_time)
            try:
                status = send_ws_to_android(ubr.bot_username, data)
            except Exception:
                continue
            if status == SUCCESS:
                logger.info(u"任务发送成功, client_id: %s." % qun.client_id)
            else:
                logger.info(u"任务发送失败, client_id: %s." % qun.client_id)

    def stop(self):
        logger.info(u"停止进程")
        self.go_work = False


free_qun_check_task_thread = FreeQunCheckThread(thread_id='vip checkout task')
