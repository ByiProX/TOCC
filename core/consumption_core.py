# -*- coding: utf-8 -*-

# IDE问题，import time无报错
import time
import threading

from datetime import datetime
from sqlalchemy import desc

from configs.config import PRODUCTION_CIRCLE_INTERVAL, db, CONSUMPTION_CIRCLE_INTERVAL
from core.message_core import analysis_and_save_a_message
from core.qun_manage import check_whether_message_is_add_qun
from core.send_task_and_ws_setting import send_task_to_ws
from core.user import check_whether_message_is_add_friend
from models.android_db import AMessage
from models.production_consumption import ProductionStatistic, ConsumptionTask, ConsumptionStatistic


class ConsumptionThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True
        self.run_start_time = None
        self.run_end_time = None

    def run(self):
        print("Start thread id: %s." % str(self.thread_id))
        self.run_start_time = datetime.now()

        while self.go_work:
            circle_start_time = time.time()

            ct_list = db.session.query(ConsumptionTask).all()

            for i, each_task in enumerate(ct_list):
                send_task_to_ws(each_task)

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
        print("End thread id: %s." % str(self.thread_id))
        self.run_end_time = datetime.now()

    def stop(self):
        self.go_work = False


consumption_thread = ConsumptionThread(thread_id='zBh8cb6VK11w6F1l')
