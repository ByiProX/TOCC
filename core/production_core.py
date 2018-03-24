# -*- coding: utf-8 -*-

# IDE问题，import time无报错
import traceback

import time
import threading
import logging

from datetime import datetime, timedelta
from sqlalchemy import desc

from configs.config import GLOBAL_RULES_UPDATE_FLAG, GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG, \
    GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG, GLOBAL_NOTICE_UPDATE_FLAG
from core.coin_wallet_core import check_whether_message_is_a_coin_wallet
from core.matching_rule_core import get_gm_rule_dict, match_message_by_rule, get_gm_default_rule_dict
from core.message_core import analysis_and_save_a_message, count_msg_by_create_time
from core.qun_manage_core import check_whether_message_is_add_qun, check_is_removed, check_whether_message_is_add_qun_v2
from core.real_time_quotes_core import match_message_by_coin_keyword
from core.synchronous_announcement_core import match_which_user_should_get_notice
from core.user_core import check_whether_message_is_add_friend, check_whether_message_is_add_friend_v2
from core.welcome_message_core import check_whether_message_is_friend_into_qun
from configs.config import PRODUCTION_CIRCLE_INTERVAL, db, MSG_TYPE_TXT, MSG_TYPE_SYS
from models.android_db_models import AMessage
from models.message_ext_models import MessageAnalysis
from models.production_consumption_models import ProductionStatistic
from sqlalchemy import orm as sql_orm

logger = logging.getLogger('main')


class ProductionThread(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.go_work = True
        self.run_start_time = None
        self.run_end_time = None
        self.last_a_message_id = None
        self.last_a_message_create_time = None

    def run(self):
        logger.info(u"Start thread id: %s." % str(self.thread_id))
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
                self.last_a_message_create_time = datetime.now() - timedelta(days = 365 * 10)

        # 第一次读取用户设置词
        gm_rule_dict = get_gm_rule_dict()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = False

        # 第一次读取统一设置词
        gm_default_rule_dict = get_gm_default_rule_dict()
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG] = False

        while self.go_work:
            try:
                circle_start_time = time.time()
                message_list = db.session.query(AMessage). \
                    filter(AMessage.create_time > self.last_a_message_create_time). \
                    order_by(AMessage.create_time.asc()).all()
                # filter(AMessage.id > self.last_a_message_id). \

                # 每次循环时，如果全局锁发生变更，则重新读取规则
                if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG]:
                    gm_rule_dict = get_gm_rule_dict()
                    GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = False

                if GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG]:
                    gm_default_rule_dict = get_gm_default_rule_dict()
                    GLOBAL_RULES_UPDATE_FLAG[GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG] = False

                # 这个是
                for each_platform, whether_should_execute in \
                        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_NOTICE_UPDATE_FLAG].items():
                    if whether_should_execute:
                        match_which_user_should_get_notice(each_platform)
                        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_NOTICE_UPDATE_FLAG][each_platform] = False
                message_analysis_list = list()
                # if len(message_list) != 0:
                #     ProductionThread._process_a_msg_list(message_list, message_analysis_list)
                if len(message_list) != 0:
                    for i, a_message in enumerate(message_list):
                        message_analysis = analysis_and_save_a_message(a_message)
                        if not message_analysis:
                            continue
                        message_analysis_list.append(message_analysis)

                        # 判断这个机器人说的话是否是文字或系统消息
                        if message_analysis.type == MSG_TYPE_TXT or message_analysis.type == MSG_TYPE_SYS:
                            pass
                        else:
                            continue

                        # 这个机器人说的话
                        # TODO 当有两个机器人的时候，这里不仅要判断是否是自己说的，还是要判断是否是其他机器人说的
                        if message_analysis.is_send == 1:
                            continue

                        # is_add_friend
                        is_add_friend = check_whether_message_is_add_friend(message_analysis)
                        is_add_friend = check_whether_message_is_add_friend_v2(message_analysis)
                        if is_add_friend:
                            continue

                        # 检查信息是否为加了一个群
                        is_add_qun = check_whether_message_is_add_qun(message_analysis)
                        is_add_qun = check_whether_message_is_add_qun_v2(message_analysis)
                        if is_add_qun:
                            continue

                        # is_removed
                        is_removed = check_is_removed(message_analysis)
                        if is_removed:
                            continue

                        # is_a_coin_wallet
                        is_a_coin_wallet = check_whether_message_is_a_coin_wallet(message_analysis)
                        if is_a_coin_wallet:
                            continue

                        # 检测是否是别人的进群提示
                        is_friend_into_qun = check_whether_message_is_friend_into_qun(message_analysis)

                        # 根据规则和内容进行匹配，并生成任务
                        rule_status = match_message_by_rule(gm_rule_dict, message_analysis)
                        if rule_status is True:
                            continue
                        else:
                            pass

                        # 对内容进行判断，是否为查询比价的情况
                        coin_price_status = match_message_by_coin_keyword(gm_default_rule_dict, message_analysis)
                        if coin_price_status is True:
                            continue

                    # 处理完毕后将新情况存入
                    self.last_a_message_id = message_list[-1].id
                    self.last_a_message_create_time = message_list[-1].create_time

                    # 更新循环情况
                    for i, message_analysis in enumerate(message_analysis_list):
                        db.session.merge(message_analysis)
                else:
                    pass

                new_pro_stat = ProductionStatistic()
                new_pro_stat.last_a_message_id = self.last_a_message_id
                new_pro_stat.last_a_message_create_time = self.last_a_message_create_time
                new_pro_stat.create_time = datetime.now()
                db.session.add(new_pro_stat)
                db.session.commit()

                if message_analysis_list:
                    msg_count_thread = threading.Thread(target = count_msg_by_create_time,
                                                        name = u'MsgCountThread',
                                                        args = (message_analysis_list[0].create_time,
                                                                message_analysis_list[-1].create_time))
                    msg_count_thread.setDaemon(True)
                    msg_count_thread.start()

                circle_now_time = time.time()
                time_to_rest = PRODUCTION_CIRCLE_INTERVAL - (circle_now_time - circle_start_time)
                if time_to_rest > 0:
                    time.sleep(time_to_rest)
                else:
                    pass
            except sql_orm.exc.ObjectDeletedError:
                logger.critical("原a_message的id对应的条目不存在")
                logger.critical("暂时不对该问题进行处理")
                logger.critical(traceback.format_exc())
                self.go_work = False
                logger.critical("循环停止运行")
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

    @staticmethod
    def _process_a_msg_list(message_list, message_analysis_list = None):
        if message_analysis_list is None:
            message_analysis_list = list()
        for i, a_message in enumerate(message_list):
            message_analysis = MessageAnalysis.analysis_and_save_a_message(a_message)
            if not message_analysis:
                continue
            message_analysis_list.append(message_analysis)

            # 判断这个机器人说的话是否是文字或系统消息
            if message_analysis.type == MSG_TYPE_TXT or message_analysis.type == MSG_TYPE_SYS:
                pass
            else:
                continue

            # 这个机器人说的话
            # TODO 当有两个机器人的时候，这里不仅要判断是否是自己说的，还是要判断是否是其他机器人说的
            if message_analysis.is_send == 1:
                continue

            # is_add_friend
            is_add_friend = MessageAnalysis.check_whether_message_is_add_friend(message_analysis)
            if is_add_friend:
                continue

            # 检查信息是否为加了一个群
            is_add_qun = MessageAnalysis.check_whether_message_is_add_qun(message_analysis)
            if is_add_qun:
                continue

            # is_removed
            is_removed = MessageAnalysis.check_is_removed(message_analysis)
            if is_removed:
                continue

            # 检测是否是别人的进群提示
            # is_friend_into_qun = MessageAnalysis.check_whether_message_is_friend_into_qun(message_analysis)

        return message_analysis_list


production_thread = ProductionThread(thread_id = 'pcwiyQgeoilnoBkS')
