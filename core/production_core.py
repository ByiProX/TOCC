# -*- coding: utf-8 -*-

# IDE问题，import time无报错
import time
import threading

from datetime import datetime, timedelta
from sqlalchemy import desc

from configs.config import PRODUCTION_CIRCLE_INTERVAL, db
from core.message_core import analysis_and_save_a_message
from core.qun_manage import check_whether_message_is_add_qun, check_is_removed
from core.user import check_whether_message_is_add_friend
from models.android_db import AMessage
from models.production_consumption import ProductionStatistic


class ProductionThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True
        self.run_start_time = None
        self.run_end_time = None
        self.last_a_message_id = None
        self.last_a_message_create_time = None

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print("Start thread id: %s." % str(self.thread_id))
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
            circle_start_time = time.time()
            # 这里先读Message，如果没读到，就什么都不做，等时间
            # 如果还不是，那么就需要去库中读筛选逻辑
            # 读完筛选逻辑后，把Message处理一下，形成任务，存入任务表
            # 循环结束
            # 检查信息是否为加bot为好友逻辑

            message_list = db.session.query(AMessage). \
                filter(AMessage.id > self.last_a_message_id). \
                order_by(AMessage.id).all()

            if len(message_list) != 0:
                message_analysis_list = list()
                for i, a_message in enumerate(message_list):
                    message_analysis = analysis_and_save_a_message(a_message)
                    if not message_analysis:
                        # TODO logger
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
        print("End thread id: %s." % str(self.thread_id))
        self.run_end_time = datetime.now()

    def stop(self):
        self.go_work = False


production_thread = ProductionThread(thread_id='pcwiyQgeoilnoBkS')
