# -*- coding: utf-8 -*-
import threading
import logging
import time
from models_v2.base_model import BaseModel
from configs.config import TIMED_BATCH_SENDING_INTERVAL, BATCH_SEND_TASK_STATUS_3, BATCH_SEND_TASK_STATUS_4
from core_v2.send_msg import send_ws_to_android
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
            free_clients = BaseModel.fetch_all("client", "*",
                                               where_clause=BaseModel.and_(
                                                   ["=", "qun_count", 1],
                                               ))

            free_clients_id = [free_client.client_id for free_client in free_clients]

            cur_time = int(time.time())
            quns = BaseModel.fetch_all("client_qun_r", "*",
                                       where_clause=BaseModel.and_(
                                           ["in", "client_id", free_clients_id],
                                           [">", "create_time", cur_time - 28 * 60],
                                           ["<", "create_time", cur_time - 25 * 60]),
                                       order_by=BaseModel.order_by({"create_time": "ASC"})
                                       )
            if not quns:
                time.sleep(60)
                continue
            for qun in quns:
                if not qun.is_paid:
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

            # time.sleep(120)
            # 重新查表，检查是否缴费
            quns = BaseModel.fetch_all("client_qun_r", "*",
                                       where_clause=BaseModel.and_(
                                           ["in", "client_id", free_clients_id],
                                           [">", "create_time", cur_time - 28 * 60],
                                           ["<", "create_time", cur_time - 25 * 60]),
                                       order_by=BaseModel.order_by({"create_time": "ASC"})
                                       )
            for qun in quns:
                if not qun.is_paid:
                    ubr = BaseModel.fetch_one(UserBotR, '*',
                                              where_clause=BaseModel.where_dict({"client_id": qun.client_id}))

                    data = {
                        "task": "退群",
                        "to": "%s" % qun.client_id,
                        "type": 1,
                        "content": "%s 尚未缴费, 请及时付款，否则2分钟后该群服务消失" % qun.chatroomname
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

    @staticmethod
    def check_whether_paid_now(qun):
        not_paid_qun_list = BaseModel.fetch_all("client_qun_r", "*",
                                                where_clause=BaseModel.and_(
                                                    ["=", "is_vip", 1],
                                                    [">", "qun_used_count", 1]),
                                                order_by=BaseModel.order_by({"create_time": "ASC"})
                                                )

    def stop(self):
        logger.info(u"停止进程")
        self.go_work = False


vip_check_task_thread = VipCheckThread(thread_id='vip checkout task')
