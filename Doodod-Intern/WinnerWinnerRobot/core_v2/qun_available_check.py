# -*- coding: utf-8 -*-
__author__ = "Quentin"

import threading
import logging
import time
from models_v2.base_model import BaseModel
from core_v2.send_msg import send_ws_to_android
from configs.config import SUCCESS, UserBotR

from utils.wkx_test_log import MyLogging

logger = logging.getLogger('main')
wkx_logger = MyLogging()


class QunAvailableCheckThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True

    def run(self):
        logger.info(u"Start thread id: %s." % str(self.thread_id))
        logger.info(u"群检测入口 thread run")
        while self.go_work:
            logger.info("进入循环 go work")

            clients = BaseModel.fetch_all("client", "*")
            clients = [client for client in clients if client.qun_used > client.qun_count]

            if not clients:
                time.sleep(60)
                continue

            clients_id = [client.client_id for client in clients]

            self.update_client_qun_used(clients_id)

            cur_time = int(time.time())
            # 查找免费用户的多余群(未付费群)，--- 半小时内
            not_paid_quns = self.check_not_paid_quns(clients_id, cur_time)

            if not_paid_quns:
                # 通知付款
                self.inform_to_pay(not_paid_quns)
            else:
                time.sleep(60)
                continue

            # 重新查表，查找未缴费群，然后退群并删除表中的记录
            not_paid_quns_again = self.check_not_paid_quns(clients_id, cur_time)

            if not_paid_quns_again:
                self.kick_out(not_paid_quns_again)
                self.update_client_qun_used(clients_id)
            else:
                time.sleep(60)
                continue

    @staticmethod
    def check_not_paid_quns(clients_id, cur_time):
        not_paid_quns = BaseModel.fetch_all("client_qun_r", "*",
                                            where_clause=BaseModel.and_(
                                                ["in", "client_id", clients_id],
                                                ["=", "is_paid", 0],
                                                ["=", "status", 1],
                                                [">", "create_time", cur_time - 30 * 60],
                                                ["<", "create_time", cur_time - 15 * 60],
                                            ),
                                            order_by=BaseModel.order_by({"create_time": "ASC"})
                                            )
        print ":>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        print not_paid_quns
        return not_paid_quns

    @staticmethod
    def inform_to_pay(quns):
        for qun in quns:
            ubr = BaseModel.fetch_one(UserBotR, '*',
                                      where_clause=BaseModel.where_dict({"client_id": qun.client_id}))

            username = BaseModel.fetch_one("client_member", "*",
                                           where_clause=BaseModel.and_(
                                               ["=", "client_id", qun.client_id]
                                           )).username

            chatroomname = BaseModel.fetch_one("a_chatroom", "*",
                                               where_clause=BaseModel.and_(
                                                   ["=", "chatroomname", qun.chatroomname]
                                               )).nickname_real

            chatroomname = chatroomname if chatroomname else u"您刚刚创建的群"

            data = {
                "task": "send_message",
                "to": username,
                "type": 1,
                "content": u"亲，30分钟快到了，我舍不得离开---%s---哦，您快快联系我们客户mm，激活小助手哦。" % chatroomname
            }

            try:
                status = send_ws_to_android(ubr.bot_username, data)
                # TODO 推送微信客服名片
                # code ...

            except Exception:
                continue

            if status == SUCCESS:
                logger.info(u"任务发送成功, client_id: %s." % qun.client_id)
            else:
                logger.info(u"任务发送失败, client_id: %s." % qun.client_id)
            # 减小安卓服务器压力
            # time.sleep(0.1)

            sleep_time = 20 * 60 - (int(time.time()) - qun.create_time) \
                if 20 * 60 - (int(time.time()) - qun.create_time) > 0 else 0
            # sleep_time = 60
            time.sleep(sleep_time)

    @staticmethod
    def kick_out(quns):
        for qun in quns:
            ubr = BaseModel.fetch_one(UserBotR, '*',
                                      where_clause=BaseModel.where_dict({"client_id": qun.client_id}))

            username = BaseModel.fetch_one("client_member", "*",
                                           where_clause=BaseModel.and_(
                                               ["=", "client_id", qun.client_id]
                                           )).username
            try:
                chatroomname = BaseModel.fetch_one("a_chatroom", "*",
                                                   where_clause=BaseModel.and_(
                                                       ["=", "chatroomname", qun.chatroomname]
                                                   )).nickname_real
            except AttributeError:
                chatroomname = u"您刚刚创建的群"

            info_data_before_leave = {
                "task": "send_message",
                "to": username,
                "type": 1,
                "content": u"轻轻地我离开了%s，正如我轻轻地来，挥一挥手，不带走一片云彩，我们有缘再见。" % chatroomname
            }

            data = {
                "task": "quit_chatroom",
                "chatroomname": qun.chatroomname
            }

            sleep_time = 28 * 60 - (int(time.time()) - qun.create_time) \
                if 28 * 60 - (int(time.time()) - qun.create_time) > 0 else 0

            # sleep_time = 60
            time.sleep(sleep_time)

            try:
                status = send_ws_to_android(ubr.bot_username, info_data_before_leave)
                if status == SUCCESS:
                    logger.info(u"退群前通知任务发送成功, client_id: %s." % qun.client_id)
                else:
                    logger.info(u"退群前通知任务发送失败, client_id: %s." % qun.client_id)
            except Exception:
                pass

            time.sleep(2)

            try:
                status = send_ws_to_android(ubr.bot_username, data)
            except Exception:
                continue

            if status == SUCCESS:
                logger.info(u"退群任务发送成功, client_id: %s." % qun.client_id)
            else:
                logger.info(u"退群任务发送失败, client_id: %s." % qun.client_id)
            # 退群并修改client_qun_r中status的记录
            qun.status = 0
            qun.save()

    @staticmethod
    def update_client_qun_used(clients_id):
        for client_id in clients_id:
            qun_used_count = BaseModel.count("client_qun_r",
                                             where_clause=BaseModel.and_(
                                                 ["=", "client_id", client_id],
                                                 ["=", "status", 1]
                                             ))

            qun_count = BaseModel.count("client_qun_r",
                                        where_clause=BaseModel.and_(
                                            ["=", "client_id", client_id],
                                            ["=", "status", 1],
                                            ["=", "is_paid", 1]
                                        ))
            client_table = BaseModel.fetch_one("client", "*",
                                               where_clause=BaseModel.and_(
                                                   ["=", "client_id", client_id]
                                               ))
            client_table.qun_used = qun_used_count
            client_table.qun_count = qun_count
            client_table.save()

    def stop(self):
        logger.info(u"停止进程")
        self.go_work = False


qun_available_check_task_thread = QunAvailableCheckThread(thread_id='qun available checkout task')
