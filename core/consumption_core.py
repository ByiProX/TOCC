# -*- coding: utf-8 -*-

# IDE问题，import time无报错
import json
import random
import traceback

import time
import threading
import logging

from datetime import datetime

from configs.config import db, CONSUMPTION_CIRCLE_INTERVAL, ERR_WRONG_USER_ITEM, ERR_WRONG_ITEM, SUCCESS, TASK_SEND_TYPE
from core.send_task_and_ws_setting_core import send_task_content_to_ws
from maintenance.setting_by_manual import SetBotRelSettingByManual
from models.android_db_models import AContact
from models.material_library_models import MaterialLibraryUser
from models.production_consumption_models import ConsumptionTask, ConsumptionStatistic, \
    ConsumptionTaskStream
from models.qun_friend_models import UserQunRelateInfo, UserQunBotRelateInfo
from models.user_bot_models import BotInfo, UserBotRelateInfo, UserInfo
from utils.u_transformat import str_to_unicode

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
            SetBotRelSettingByManual.set_bot_info_by_a_bot_db()
            bot_info_new = db.session.query(BotInfo).filter(BotInfo.username == self.bot_username).first()
            if not bot_info_new:
                raise ValueError("没有该bot，无法启动")

    def run(self):
        logger.info(u"Start thread id: %s." % str(self.thread_id))
        self.run_start_time = datetime.now()

        while self.go_work:
            try:
                circle_start_time = time.time()

                ct_list = db.session.query(ConsumptionTask).filter(ConsumptionTask.bot_username == self.bot_username). \
                    order_by(ConsumptionTask.task_id).all()

                for i, each_task in enumerate(ct_list):
                    if each_task.task_type in [1, 2, 5, 6, 7]:
                        task_send_content = json.loads(each_task.task_send_content)
                        if each_task.task_send_type == TASK_SEND_TYPE['text']:

                            send_task_content_to_ws(each_task.bot_username, each_task.chatroomname,
                                                    each_task.task_send_type, task_send_content['text'])
                            time.sleep(random.random() + 0.6)
                        else:
                            logger.error("目前不支持其他类型发送")
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


def add_task_to_consumption_task(uqr_info, um_lib, user_id, task_type, task_relevant_id,
                                 message_said_username_list=None):
    if not isinstance(uqr_info, UserQunRelateInfo):
        raise TypeError
    if not isinstance(um_lib, MaterialLibraryUser):
        raise TypeError

    c_task = ConsumptionTask()
    c_task.qun_owner_user_id = uqr_info.user_id
    c_task.task_initiate_user_id = user_id
    c_task.chatroomname = uqr_info.chatroomname
    c_task.task_type = task_type
    c_task.task_relevant_id = task_relevant_id

    c_task.task_send_type = um_lib.task_send_type

    # 组装content
    if c_task.task_send_type == TASK_SEND_TYPE['text']:
        if message_said_username_list is None:
            c_task.task_send_content = um_lib.task_send_content
        else:
            send_content = json.loads(um_lib.task_send_content)
            text = send_content.get("text")
            res_text = u""
            for message_said_username in message_said_username_list:
                a_contact = db.session.query(AContact).filter(AContact.username == message_said_username).first()
                if not a_contact:
                    logger.error(u"无法找到该人名称")
                    nickname = u""
                else:
                    nickname = str_to_unicode(a_contact.nickname)
                res_text += u"@" + nickname + u" "
            c_task.task_send_content = json.dumps({"text": (res_text + text)})
    else:
        logger.error("目前无法发送其他类型")
        return ERR_WRONG_ITEM

    # 目前一个人只能有一个机器人，所以此处不进行机器人选择；未来会涉及机器人选择问题
    uqbr_info_list = db.session.query(UserQunBotRelateInfo).filter(
        UserQunBotRelateInfo.uqun_id == uqr_info.uqun_id).all()
    if not uqbr_info_list:
        logger.error(u"没有找到群与机器人绑定关系. qun_id: %s." % uqr_info.uqun_id)
        return ERR_WRONG_USER_ITEM
    user_bot_rid_list = []
    for uqbr_info in uqbr_info_list:
        if uqbr_info.is_error is True:
            continue
        else:
            user_bot_rid_list.append(uqbr_info.user_bot_rid)
    # 目前只要读取到一个bot_id就好
    bot_id = None
    for user_bot_rid in user_bot_rid_list:
        ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_bot_rid == user_bot_rid).all()
        bot_id = ubr_info[0].bot_id
        if bot_id:
            break

    bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == bot_id).first()
    if not bot_info:
        logger.error(u"没有找到bot相关信息. bot_id: %s." % bot_id)
        return ERR_WRONG_ITEM

    c_task.bot_username = bot_info.username
    now_time = datetime.now()
    c_task.message_received_time = now_time
    c_task.task_create_time = now_time

    db.session.add(c_task)
    db.session.commit()
    return SUCCESS

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
