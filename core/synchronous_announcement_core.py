# -*- coding: utf-8 -*-
import json
import logging

from datetime import datetime

from configs.config import ERR_WRONG_FUNC_STATUS, db, SUCCESS, ERR_WRONG_ITEM, CONSUMPTION_TASK_TYPE, TASK_SEND_TYPE
from models.production_consumption_models import ConsumptionTask
from models.qun_friend_models import UserQunRelateInfo, UserQunBotRelateInfo
from models.synchronous_announcement_models import SynchronousAnnouncementDefaultSettingInfo, \
    SynchronousAnnouncementDSUserRelate, BlockCCCrawlNotice
from models.user_bot_models import UserBotRelateInfo, BotInfo

logger = logging.getLogger('main')


def switch_func_synchronous_announcement(user_info, switch):
    """
    打开或关闭实时报价功能
    :param user_info:
    :param switch:
    :return:
    """
    if user_info.func_synchronous_announcement and switch:
        logger.error("目前已为开启状态，无需再次开启")
        return ERR_WRONG_FUNC_STATUS
    if not user_info.func_synchronous_announcement and not switch:
        logger.error("目前已为关闭状态，无需再次开启")
        return ERR_WRONG_FUNC_STATUS

    if switch is True:
        sa_info_list = db.session.query(SynchronousAnnouncementDefaultSettingInfo).all()
        for sa_info in sa_info_list:
            sa_user_rel = SynchronousAnnouncementDSUserRelate()
            sa_user_rel.ds_id = sa_info.ds_id
            sa_user_rel.user_id = user_info.user_id
            sa_user_rel.create_time = datetime.now()
            db.session.add(sa_user_rel)
        user_info.func_synchronous_announcement = True
        db.session.commit()
    elif switch is False:
        sa_user_rel_list = db.session.query(SynchronousAnnouncementDSUserRelate).filter(
            SynchronousAnnouncementDSUserRelate.user_id == user_info.user_id).all()

        for sa_user_rel in sa_user_rel_list:
            db.session.delete(sa_user_rel)

        user_info.func_synchronous_announcement = False
        db.session.commit()

    return SUCCESS


def get_s_announcement_list_and_status(user_info):
    sa_info_list = db.session.query(SynchronousAnnouncementDefaultSettingInfo).all()

    res = []
    for sa_info in sa_info_list:
        res_dict = {}
        res_dict.setdefault("platform_id", sa_info.ds_id)
        res_dict.setdefault("platform_name", sa_info.platform_name)
        res_dict.setdefault("logo", sa_info.platform_icon)

        ts = db.session.query(SynchronousAnnouncementDSUserRelate).filter(
            SynchronousAnnouncementDSUserRelate.ds_id == sa_info.ds_id,
            SynchronousAnnouncementDSUserRelate.user_id == user_info.user_id).first()
        if ts:
            res_dict.setdefault("is_take_effect", True)
        else:
            res_dict.setdefault("is_take_effect", False)

        res.append(res_dict)

    return SUCCESS, res, user_info.func_synchronous_announcement


def switch_a_s_announcement_effect(user_info, platform_id, switch):
    if not user_info.func_synchronous_announcement:
        logger.error("该用户尚未开启该功能")
        return ERR_WRONG_FUNC_STATUS

    ts = db.session.query(SynchronousAnnouncementDSUserRelate).filter(
        SynchronousAnnouncementDSUserRelate.ds_id == platform_id,
        SynchronousAnnouncementDSUserRelate.user_id == user_info.user_id).first()
    if ts:
        old_switch = True
    else:
        old_switch = False

    if old_switch and switch:
        logger.error("目前已为开启状态，无需再次开启")
        return ERR_WRONG_FUNC_STATUS
    if not old_switch and not switch:
        logger.error("目前已为关闭状态，无需再次开启")
        return ERR_WRONG_FUNC_STATUS

    if switch is True:
        sa_user_rel = SynchronousAnnouncementDSUserRelate()
        sa_user_rel.ds_id = platform_id
        sa_user_rel.user_id = user_info.user_id
        sa_user_rel.create_time = datetime.now()
        db.session.add(sa_user_rel)
    elif switch is False:
        sa_user_rel = db.session.query(SynchronousAnnouncementDSUserRelate).filter(
            SynchronousAnnouncementDSUserRelate.user_id == user_info.user_id,
            SynchronousAnnouncementDSUserRelate.ds_id == platform_id).first()

        if not sa_user_rel:
            logger.error("不应没有该项目")
            return ERR_WRONG_ITEM

        db.session.delete(sa_user_rel)
    db.session.commit()
    return SUCCESS


def match_which_user_should_get_notice(platform_name):
    # 读取平台
    sa_info = db.session.query(SynchronousAnnouncementDefaultSettingInfo).filter(
        SynchronousAnnouncementDefaultSettingInfo.platform_name == platform_name).first()

    if not sa_info:
        logger.critical(u"没有找到对应的平台. platform_name: %s." % platform_name)
        return ERR_WRONG_ITEM
    ds_id = sa_info.ds_id

    # 读取更新的信息
    if sa_info.platform_name == "blockcc":
        crawler_database = BlockCCCrawlNotice

        wait_to_send_info_list = db.session.query(crawler_database).filter(crawler_database.is_handled == 0).all()
    else:
        logger.critical("目前暂不支持其他平台数据")
        return ERR_WRONG_ITEM

    # 读取需要更新的群和对应的机器人
    sa_user_relate_list = db.session.query(SynchronousAnnouncementDSUserRelate).filter(
        SynchronousAnnouncementDSUserRelate.ds_id == ds_id).all()
    # 暂时是该人的所有群均可收到该消息
    for sa_user_relate in sa_user_relate_list:
        user_id = sa_user_relate.user_id
        uqun_info_list = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == user_id,
                                                                    UserQunRelateInfo.is_deleted == 0).all()
        for uqun_info in uqun_info_list:
            uqun_id = uqun_info.uqun_id
            chatroomname = uqun_info.chatroomname
            uqbr_info_list = db.session.query(UserQunBotRelateInfo).filter(UserQunBotRelateInfo.uqun_id == uqun_id,
                                                                           UserQunBotRelateInfo.is_error == 0).all()
            if not uqbr_info_list:
                logger.error(u"没有该群对应的群关系. uqun_id: %s." % uqun_id)
                return ERR_WRONG_ITEM
            for uqbr_info in uqbr_info_list:
                ubr_info = db.session.query(UserBotRelateInfo).filter(
                    UserBotRelateInfo.user_bot_rid == uqbr_info.user_bot_rid).first()
                if not ubr_info:
                    logger.error(u"没有找到对应的机器人关系. user_bot_rid: %s." % uqbr_info.user_bot_rid)
                    return ERR_WRONG_ITEM
                bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == ubr_info.bot_id).first()
                if not bot_info:
                    logger.error(u"没有找到对应的机器人. bot_id: %s." % ubr_info.bot_id)
                bot_username = bot_info.username

                for wait_to_send_info in wait_to_send_info_list:
                    now_time = datetime.now()
                    c_task = ConsumptionTask()
                    c_task.qun_owner_user_id = uqun_info.user_id
                    c_task.task_initiate_user_id = user_id
                    c_task.chatroomname = chatroomname
                    c_task.task_type = CONSUMPTION_TASK_TYPE['synchronous_announcement']
                    c_task.task_relevant_id = ds_id
                    c_task.task_send_type = TASK_SEND_TYPE['text']

                    if len(wait_to_send_info.description) >= 105:
                        res_text = u"《" + wait_to_send_info.title + u"》\n来源：" + wait_to_send_info.from_source + \
                                   u"\n\n" + wait_to_send_info.description[:100] + u"...\n\n" + \
                                   wait_to_send_info.origin_url + u"\n" + unicode(datetime.now())[:19]
                    else:
                        res_text = u"《" + wait_to_send_info.title + u"》\n来源：" + wait_to_send_info.from_source + \
                                   u"\n\n" + wait_to_send_info.description + u"\n\n" + \
                                   wait_to_send_info.origin_url + u"\n" + unicode(datetime.now())[:19]

                    c_task.task_send_content = json.dumps({"text": res_text})
                    c_task.bot_username = bot_username
                    c_task.message_received_time = now_time
                    c_task.task_create_time = now_time

                    db.session.add(c_task)
                    db.session.commit()

    for wait_to_send_info in wait_to_send_info_list:
        wait_to_send_info.is_handled = True
        db.session.merge(wait_to_send_info)
    db.session.commit()
    return SUCCESS
