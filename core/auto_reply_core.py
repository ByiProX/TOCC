# -*- coding: utf-8 -*-
import logging

from copy import deepcopy
from datetime import datetime

from configs.config import db, ERR_WRONG_USER_ITEM, SUCCESS, GLOBAL_RULES_UPDATE_FLAG, ERR_WRONG_FUNC_STATUS, \
    ERR_WRONG_ITEM, CONSUMPTION_TASK_TYPE, GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG
from core.consumption_core import add_task_to_consumption_task
from core.material_library_core import generate_material_into_frontend_by_material_id, \
    analysis_frontend_material_and_put_into_mysql
from core.qun_manage_core import get_a_chatroom_dict_by_uqun_id
from models.android_db_models import AContact
from models.auto_reply_models import AutoReplySettingInfo, AutoReplyTargetRelate, AutoReplyMaterialRelate, \
    AutoReplyKeywordRelateInfo
from models.matching_rule_models import GlobalMatchingRule
from models.material_library_models import MaterialLibraryUser
from models.qun_friend_models import UserQunRelateInfo
from models.user_bot_models import UserInfo
from utils.u_time import datetime_to_timestamp_utc_8

logger = logging.getLogger('main')


# def read_func_auto_reply_status():
#     """
#     读取自动回复和智能回复的状态
#     :return:
#     """


def switch_func_auto_reply(user_info, switch):
    """
    打开或关闭自动回复功能
    :return:
    """
    if user_info.func_auto_reply and switch:
        logger.error("目前已为开启状态，无需再次开启")
        return ERR_WRONG_FUNC_STATUS
    if not user_info.func_auto_reply and not switch:
        logger.error("目前已为关闭状态，无需再次开启")
        return ERR_WRONG_FUNC_STATUS

    switch_choose = [True, False]
    for choose in switch_choose:
        if switch == choose:
            ar_setting_info_list = db.session.query(AutoReplySettingInfo).filter(
                AutoReplySettingInfo.user_id == user_info.user_id,
                AutoReplySettingInfo.is_deleted == 0).all()
            for ar_setting_info in ar_setting_info_list:
                ar_setting_info.is_take_effect = choose
                db.session.merge(ar_setting_info)

            gm_rule_list = db.session.query(GlobalMatchingRule).filter(
                GlobalMatchingRule.user_id == user_info.user_id,
                GlobalMatchingRule.task_type == CONSUMPTION_TASK_TYPE['auto_reply']).all()
            for gm_rule in gm_rule_list:
                gm_rule.is_take_effect = choose
                db.session.merge(gm_rule)

            user_info.func_auto_reply = choose
            db.session.merge(user_info)
            db.session.commit()
            GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = True

    return SUCCESS


# def switch_func_auto_reply_default_setting():
#     """
#     打开或关闭只能回复功能
#     :return:
#     """


# def switch_a_auto_reply_setting_take_effect():
#     """
#     打开或关闭某一条自动回复的按钮
#     :return:
#     """


# def switch_a_default_auto_reply_setting_take_effect():
#     """
#     打开或关闭某一条系统模板的按钮
#     :return:
#     """


def get_auto_reply_setting(user_info):
    """
    得到一个人的所有自动回复设置
    :return:
    """
    ar_setting_info_list = db.session.query(AutoReplySettingInfo).filter(
        AutoReplySettingInfo.user_id == user_info.user_id).filter(AutoReplySettingInfo.is_deleted == 0).order_by(
        AutoReplySettingInfo.setting_create_time.desc()).all()

    result = []
    for ar_setting_info in ar_setting_info_list:
        status, task_detail_res = get_setting_detail(ar_setting_info)
        if status == SUCCESS:
            result.append(deepcopy(task_detail_res))
        else:
            logger.error(u"部分任务无法读取. setting_id: %s." % ar_setting_info.setting_id)
    return SUCCESS, result


# def get_default_auto_reply_setting():
#     """
#     读取一个人的只能回复内容的页面
#     :return:
#     """


def get_setting_detail(ar_setting_info):
    """
    读取一个任务的所有信息
    :return:
    """
    res = dict()
    res.setdefault("setting_id", ar_setting_info.setting_id)
    res.setdefault("task_covering_chatroom_count", ar_setting_info.task_covering_qun_count)
    res.setdefault("task_covering_people_count", ar_setting_info.task_covering_people_count)
    res.setdefault("task_create_time", datetime_to_timestamp_utc_8(ar_setting_info.setting_create_time))

    # 生成群信息
    res.setdefault("chatroom_list", [])
    ar_setting_target_list = db.session.query(AutoReplyTargetRelate).filter(
        AutoReplyTargetRelate.setting_id == ar_setting_info.setting_id).all()
    if not ar_setting_target_list:
        return ERR_WRONG_ITEM, None
    uqun_id_list = []
    for ar_setting_target in ar_setting_target_list:
        uqun_id_list.append(ar_setting_target.uqun_id)
    for uqun_id in uqun_id_list:
        status, tcd_res = get_a_chatroom_dict_by_uqun_id(uqun_id=uqun_id)
        if status == SUCCESS:
            res['chatroom_list'].append(deepcopy(tcd_res))
        else:
            pass

    # 生成material信息
    res.setdefault("message_list", [])
    ar_setting_material_list = db.session.query(AutoReplyMaterialRelate).filter(
        AutoReplyMaterialRelate.setting_id == ar_setting_info.setting_id).order_by(
        AutoReplyMaterialRelate.send_seq).all()
    if not ar_setting_material_list:
        return ERR_WRONG_ITEM, None
    material_id_list = []
    for ar_setting_material in ar_setting_material_list:
        material_id_list.append(ar_setting_material.material_id)
    for material_id in material_id_list:
        temp_material_dict = generate_material_into_frontend_by_material_id(material_id)
        res["message_list"].append(deepcopy(temp_material_dict))

    # TODO 生成keyword信息
    res.setdefault("keyword_list", [])
    ar_setting_keyword_list = db.session.query(AutoReplyKeywordRelateInfo).filter(
        AutoReplyKeywordRelateInfo.setting_id == ar_setting_info.setting_id).order_by(
        AutoReplyKeywordRelateInfo.send_seq).all()
    if not ar_setting_keyword_list:
        return ERR_WRONG_ITEM, None
    for ar_setting_keyword in ar_setting_keyword_list:
        temp_keyword_dict = dict()
        temp_keyword_dict.setdefault("keyword_content", ar_setting_keyword.keyword)
        temp_keyword_dict.setdefault("is_full_match", ar_setting_keyword.is_full_match)
        res['keyword_list'].append(deepcopy(temp_keyword_dict))

    return SUCCESS, res


def delete_a_auto_reply_setting(user_info, setting_id):
    """
    完全删除一条回复
    :return:
    """
    if not isinstance(user_info, UserInfo):
        raise TypeError
    ar_setting_info = db.session.query(AutoReplySettingInfo).filter(
        AutoReplySettingInfo.setting_id == setting_id).first()
    if not ar_setting_info:
        logger.error("没有找到该自动回复设置")
        return ERR_WRONG_ITEM
    if ar_setting_info.user_id != user_info.user_id:
        logger.error("该设置不是该用户设置")
        return ERR_WRONG_USER_ITEM
    if ar_setting_info.is_deleted:
        logger.error("该群已经被删除")
        return ERR_WRONG_ITEM

    ar_setting_info.is_take_effect = False
    ar_setting_info.is_deleted = True
    db.session.merge(ar_setting_info)
    db.session.commit()

    gm_rule_list = db.session.query(GlobalMatchingRule).filter(GlobalMatchingRule.user_id == user_info.user_id,
                                                               GlobalMatchingRule.task_type == 2,
                                                               GlobalMatchingRule.task_relevant_id == setting_id).all()
    for gm_rule in gm_rule_list:
        db.session.delete(gm_rule)
    db.session.commit()
    GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = True
    return SUCCESS


def create_a_auto_reply_setting(user_info, chatroom_list, message_list, keyword_list):
    """
    新建一条回复setting
    :return:
    """
    now_time = datetime.now()
    ar_setting_info = AutoReplySettingInfo()
    ar_setting_info.user_id = user_info.user_id
    ar_setting_info.task_covering_qun_count = 0
    ar_setting_info.task_covering_people_count = 0
    ar_setting_info.is_take_effect = True
    ar_setting_info.is_deleted = False
    ar_setting_info.setting_create_time = now_time
    db.session.add(ar_setting_info)
    db.session.commit()

    task_covering_qun_count = 0
    task_covering_people_count = 0

    valid_chatroom_list = []
    for uqun_id in chatroom_list:
        uqr_info = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == user_info.user_id,
                                                              UserQunRelateInfo.uqun_id == uqun_id).first()
        if not uqr_info:
            logger.error("没有属于该用户的该群")
            return ERR_WRONG_USER_ITEM

        a_contact = db.session.query(AContact).filter(AContact.username == uqr_info.chatroomname).first()

        if not a_contact:
            logger.error("安卓库中没有该群")
            return ERR_WRONG_USER_ITEM

        task_covering_qun_count += 1
        task_covering_people_count += a_contact.member_count

        ar_setting_target = AutoReplyTargetRelate()
        ar_setting_target.setting_id = ar_setting_info.setting_id
        ar_setting_target.uqun_id = uqun_id

        db.session.add(ar_setting_target)
        valid_chatroom_list.append(uqr_info)
    db.session.commit()

    # 处理message，入库material
    valid_material_list = []
    for i, message_info in enumerate(message_list):
        message_return, um_lib = analysis_frontend_material_and_put_into_mysql(user_info.user_id, message_info,
                                                                               now_time)
        if message_return == SUCCESS:
            pass
        elif message_return == ERR_WRONG_ITEM:
            continue

        material_id = um_lib.material_id
        ar_setting_material = AutoReplyMaterialRelate()
        ar_setting_material.setting_id = ar_setting_info.setting_id
        ar_setting_material.material_id = material_id
        ar_setting_material.send_seq = i
        db.session.add(ar_setting_material)
        valid_material_list.append(um_lib)

    db.session.commit()

    # 处理keyword
    valid_keyword_list = []
    for i, keyword_info in enumerate(keyword_list):
        ar_setting_keyword_r_info = AutoReplyKeywordRelateInfo()
        ar_setting_keyword_r_info.setting_id = ar_setting_info.setting_id

        keyword = keyword_info.get("keyword_content")
        if keyword:
            ar_setting_keyword_r_info.keyword = keyword
        else:
            logger.error("没有读取到关键词")
            continue
        is_full_match = keyword_info.get("is_full_match")
        ar_setting_keyword_r_info.is_full_match = is_full_match
        ar_setting_keyword_r_info.send_seq = i
        db.session.add(ar_setting_keyword_r_info)
        valid_keyword_list.append(ar_setting_keyword_r_info)

    # 更新主库中的数量
    ar_setting_info.task_covering_qun_count = task_covering_qun_count
    ar_setting_info.task_covering_people_count = task_covering_people_count
    db.session.merge(ar_setting_info)
    db.session.commit()

    u_flag = False
    for uqr_info_iter in valid_chatroom_list:
        for keyword_iter in valid_keyword_list:
            u_flag = True
            _add_rule_to_matching_rule(uqr_info_iter, keyword_iter, ar_setting_info)
    if u_flag:
        GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = True
    return SUCCESS


def update_a_tuto_reply_setting(user_info, chatroom_list, message_list, keyword_list, setting_id):
    """
    先将之前的删除，然后再建立一个新的任务
    """
    logger.debug(u"更新某设置，采用先删除之前的规则，后建立新规则的方式")
    status = delete_a_auto_reply_setting(user_info, setting_id)
    if status == SUCCESS:
        logger.debug(u"成功删除之前的设置.")
    else:
        logger.error(u"删除失败，不进行任务建立. setting_id: %s." % setting_id)
        return status
    status = create_a_auto_reply_setting(user_info, chatroom_list, message_list, keyword_list)
    if status == SUCCESS:
        logger.info(u"更新自动回复任务成功.")
        return SUCCESS
    else:
        logger.error(u"新建任务失败.")
        return status


def activate_rule_and_add_task_to_consumption_task(ar_setting_id, message_chatroomname, message_said_username):
    ar_setting_info = db.session.query(AutoReplySettingInfo).filter(
        AutoReplySettingInfo.setting_id == ar_setting_id).first()
    if not ar_setting_info:
        return ERR_WRONG_ITEM

    valid_chatroom_list = []
    uqr_info = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == ar_setting_info.user_id,
                                                          UserQunRelateInfo.chatroomname == message_chatroomname).\
        first()
    if not uqr_info:
        logger.error("没有属于该用户的该群")
        return ERR_WRONG_USER_ITEM
    a_contact = db.session.query(AContact).filter(AContact.username == uqr_info.chatroomname).first()
    if not a_contact:
        logger.error("安卓库中没有该群")
        return ERR_WRONG_USER_ITEM
    valid_chatroom_list.append(uqr_info)

    ar_setting_material_list = db.session.query(AutoReplyMaterialRelate).filter(
        AutoReplyMaterialRelate.setting_id == ar_setting_id).all()
    valid_material_list = []
    for ar_setting_material in ar_setting_material_list:
        um_lib = db.session.query(MaterialLibraryUser).filter(
            MaterialLibraryUser.material_id == ar_setting_material.material_id).first()
        if not um_lib:
            logger.error("素材库中没有该群")
            return ERR_WRONG_USER_ITEM
        valid_material_list.append(um_lib)

    for uqr_info_iter in valid_chatroom_list:
        for um_lib_iter in valid_material_list:
            _add_task_to_consumption_task(uqr_info_iter, um_lib_iter, ar_setting_info, message_said_username)
    return SUCCESS


def _add_task_to_consumption_task(uqr_info, um_lib, ar_setting_info, message_said_username):
    status = add_task_to_consumption_task(uqr_info, um_lib, ar_setting_info.user_id,
                                          CONSUMPTION_TASK_TYPE["auto_reply"], ar_setting_info.setting_id,
                                          message_said_username_list=[message_said_username])
    return status


def _add_rule_to_matching_rule(uqr_info, ar_setting_keyword_r_info, ar_setting_info):
    """
    将任务放入globalmatchingrule
    :param uqr_info:
    :param ar_setting_keyword_r_info:
    :param ar_setting_info:
    :return:
    """
    if not isinstance(uqr_info, UserQunRelateInfo):
        raise TypeError
    if not isinstance(ar_setting_keyword_r_info, AutoReplyKeywordRelateInfo):
        raise TypeError
    if not isinstance(ar_setting_info, AutoReplySettingInfo):
        raise TypeError

    gm_rule = GlobalMatchingRule()
    gm_rule.user_id = uqr_info.user_id
    gm_rule.chatroomname = uqr_info.chatroomname
    gm_rule.match_word = ar_setting_keyword_r_info.keyword

    gm_rule.task_type = CONSUMPTION_TASK_TYPE["auto_reply"]
    gm_rule.task_relevant_id = ar_setting_info.setting_id

    now_time = datetime.now()
    gm_rule.create_time = now_time
    gm_rule.is_exact_match = ar_setting_keyword_r_info.is_full_match
    gm_rule.is_take_effect = ar_setting_info.is_take_effect
    db.session.add(gm_rule)
    db.session.commit()
