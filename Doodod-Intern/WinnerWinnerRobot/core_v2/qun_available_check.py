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
        logger.info("群检测入口 thread run")
        while self.go_work:
            logger.info("进入循环 go work")
            # 查找使用的群数量超出购买数量的客户
            clients = BaseModel.fetch_all("client", "*",
                                          where_clause=BaseModel.and_(
                                              # ["<", "qun_count", "qun_used"],
                                              ["=", "client_id", 5]
                                          ))

            print clients
            print "clients" + str(clients.__len__())

            if not clients:
                time.sleep(60)
                print "sleep end......................."
                continue

            clients_id = [client.client_id for client in clients]
            logger.info("client_id %d" % clients_id.__len__())

            cur_time = int(time.time())
            # 查找免费用户的多余群(未付费群)，--- 半小时内
            not_paid_quns = self.check_not_paid_quns(clients_id, cur_time)
            logger.info("not_paid_quns %d" % not_paid_quns.__len__())

            if not_paid_quns:
                # 通知付款
                logger.info("into inform to pay")
                self.inform_to_pay(not_paid_quns)
                logger.info("out inform to pay")

            else:
                time.sleep(60)
                continue

            # 重新查表，查找未缴费群，然后退群并删除表中的记录
            not_paid_quns_again = self.check_not_paid_quns(clients_id, cur_time)
            logger.info("not_paid_quns_again %d" % not_paid_quns_again.__len__())

            if not_paid_quns_again:
                logger.info("into kick out")
                self.kick_out(not_paid_quns_again)
                logger.info("out kick out")

                logger.info("into update_client_qun_used")
                self.update_client_qun_used(clients_id)
                logger.info("out update_client_qun_used")
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
                                                # [">", "create_time", cur_time - 30 * 60],
                                                # ["<", "create_time", cur_time - 15 * 60],
                                            ),
                                            order_by=BaseModel.order_by({"create_time": "ASC"})
                                            )
        print ":::::::::::::::::::::::::::::::::::::::::::"
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
            # TODO to user change
            data = {
                "task": "send_message",
                "to": username,
                "type": 1,
                "content": u"%s 尚未缴费, 请及时付款，否则稍后该群服务消失" % chatroomname
            }

            # sleep_time = 20 * 60 - (int(time.time()) - qun.create_time) \
            #     if 20 * 60 - (int(time.time()) - qun.create_time) > 0 else 0
            sleep_time = 60
            time.sleep(sleep_time)

            try:
                status = send_ws_to_android(ubr.bot_username, data)
            except Exception:
                continue
            if status == SUCCESS:
                logger.info(u"任务发送成功, client_id: %s." % qun.client_id)
            else:
                logger.info(u"任务发送失败, client_id: %s." % qun.client_id)
            # 减小安卓服务器压力
            time.sleep(0.1)

    @staticmethod
    def kick_out(quns):
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

            # TODO 退群接口添加
            data = {
                "task": "send_message",
                "to": username,
                "type": 1,
                "content": u"%s 已退群" % chatroomname
            }

            sleep_time = 28 * 60 - (int(time.time()) - qun.create_time) \
                if 28 * 60 - (int(time.time()) - qun.create_time) > 0 else 0
            time.sleep(sleep_time)
            try:
                status = send_ws_to_android(ubr.bot_username, data)
            except Exception:
                continue
            if status == SUCCESS:
                logger.info(u"任务发送成功, client_id: %s." % qun.client_id)
            else:
                logger.info(u"任务发送失败, client_id: %s." % qun.client_id)
            # 退群并修改client_qun_r中status的记录
            ubr.status = 0
            ubr.save()

    @staticmethod
    def update_client_qun_used(clients_id):
        for client_id in clients_id:
            qun_used_count = BaseModel.count("client_qun_r",
                                             where_clause=BaseModel.and_(
                                                 ["=", "client_id", client_id],
                                                 ["=", "status", 1]
                                             ))
            client_table = BaseModel.fetch_one("client", "*",
                                               where_clause=BaseModel.and_(
                                                   ["=", "client_id", client_id]
                                               ))
            client_table.qun_used = qun_used_count
            client_table.save()

    def stop(self):
        logger.info(u"停止进程")
        self.go_work = False


qun_available_check_task_thread = QunAvailableCheckThread(thread_id='qun available checkout task')
