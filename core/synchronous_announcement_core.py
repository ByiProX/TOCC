# -*- coding: utf-8 -*-
import logging

from datetime import datetime

from configs.config import ERR_WRONG_FUNC_STATUS, db, SUCCESS, ERR_WRONG_ITEM
from models.synchronous_announcement_models import SynchronousAnnouncementDefaultSettingInfo, \
    SynchronousAnnouncementDSUserRelate

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
        user_info.func_real_time_quotes = True
        db.session.commit()
    elif switch is False:
        sa_user_rel_list = db.session.query(SynchronousAnnouncementDefaultSettingInfo).filter(
            SynchronousAnnouncementDefaultSettingInfo.user_id == user_info.user_id).all()

        for sa_user_rel in sa_user_rel_list:
            db.session.delete(sa_user_rel)

        user_info.func_real_time_quotes = False
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


def app_switch_a_s_announcement_effect(user_info, platform_id, switch):
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
        sa_user_rel = db.session.query(SynchronousAnnouncementDefaultSettingInfo).filter(
            SynchronousAnnouncementDefaultSettingInfo.user_id == user_info.user_id,
            SynchronousAnnouncementDefaultSettingInfo.ds_id == platform_id).first()

        if not sa_user_rel:
            logger.error("不应没有该项目")
            return ERR_WRONG_ITEM

        db.session.delete(sa_user_rel)
    db.session.commit()
    return SUCCESS
