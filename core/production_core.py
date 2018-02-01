# -*- coding: utf-8 -*-

# IDE问题，import time无报错
import time
import threading

from datetime import datetime
from config import PRODUCTION_CIRCLE_INTERVAL


class ProductionThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True
        self.run_start_time = None
        self.run_end_time = None

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print("Start thread id: %s." % str(self.thread_id))
        self.run_start_time = datetime.now()
        while self.go_work:
            circle_start_time = time.time()
            # 这里先读Message，如果没读到，就什么都不做，等时间
            # 如果读到了，那就先判断是否是入群和加群信息，如果是，走入群和加群逻辑
            # 如果还不是，那么就需要去库中读筛选逻辑
            # 读完筛选逻辑后，把Message处理一下，形成任务，存入任务表
            # 循环结束

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

# 加机器人，扫Message，找昶子

# 扫Message，进群解析，找昶子

# 扫Message，再看
