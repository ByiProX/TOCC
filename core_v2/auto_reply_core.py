# -*- coding: utf-8 -*-
import logging

from copy import deepcopy
from datetime import datetime

from configs.config import db, ERR_WRONG_USER_ITEM, SUCCESS, GLOBAL_RULES_UPDATE_FLAG, ERR_WRONG_FUNC_STATUS, \
    ERR_WRONG_ITEM, CONSUMPTION_TASK_TYPE, GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG, Keywords, Chatroom, UserSwitch
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
from models_v2.base_model import CM, BaseModel
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
    # Mark bool to int
    switch = 1 if switch else 0

    user_switch = BaseModel.fetch_one(UserSwitch, "*", where_clause = BaseModel.where("=", "client_id", user_info.client_id))
    if user_switch.func_auto_reply and switch:
        logger.error("目前已为开启状态，无需再次开启. 返回正常.")
        return SUCCESS
    if not user_switch.func_auto_reply and not switch:
        logger.error("目前已为关闭状态，无需再次开启. 返回正常.")
        return SUCCESS

    user_switch.func_auto_reply = switch
    user_switch.save()
    # GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = True

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
    user_switch = BaseModel.fetch_one(UserSwitch, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    func_auto_reply = user_switch.func_auto_reply
    keywords_info_list = BaseModel.fetch_all(Keywords, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                            "welcome": 0}))
    result = []
    for keywords_info in keywords_info_list:
        res = dict()
        keywords_dict = keywords_info.keywords
        chatroom_list = keywords_info.chatroom_list
        reply_content_list = keywords_info.reply_content
        keyword_list = list()
        for match_type, keywords in keywords_dict.iteritems():
            keyword_json = dict()
            if match_type == "precise":
                keyword_json["is_full_match"] = True
            else:
                keyword_json["is_full_match"] = False
            for keyword in keywords:
                keyword_json["keyword_content"] = keyword
                keyword_list.append(deepcopy(keyword_json))

        message_list = list()
        for reply_content in reply_content_list:
            message_json = dict()
            message_json["task_send_type"] = reply_content.get("type")
            message_json["text"] = reply_content.get("content")
            message_json["seq"] = reply_content.get("seq")
            message_list.append(message_json)

        chatroom_count = len(chatroom_list)
        chatroom_json_list = list()
        member_count = 0
        for chatroomname in chatroom_list:
            chatroom = BaseModel.fetch_one(Chatroom, "member_count", where_clause = BaseModel.where_dict({"chatroomname": chatroomname}))
            if not chatroom:
                continue
            member_count += chatroom.member_count
            chatroom_dict = dict()
            chatroom_dict['chatroom_id'] = chatroom.get_id()
            chatroom_dict['chatroom_nickname'] = chatroom.nickname
            chatroom_dict['chatroomname'] = chatroomname
            chatroom_dict['chatroom_member_count'] = chatroom.member_count
            chatroom_dict['avatar_url'] = chatroom.avatar_url
            chatroom_dict['chatroom_status'] = 0
            chatroom_json_list.append(chatroom_dict)

        res['keywords_id'] = keywords_info.get_id()
        res['keyword_list'] = keyword_list
        res['message_list'] = message_list
        res['chatroom_list'] = chatroom_json_list
        res['task_covering_chatroom_count'] = chatroom_count
        res['task_covering_people_count'] = member_count
        res['task_create_time'] = keywords_info.create_time
        result.append(res)
        # TODO: TBD
        # res['task_sended_count'] = message_list
        # res['task_sended_failed_count'] = message_list

    return SUCCESS, result, func_auto_reply


# def get_default_auto_reply_setting():
#     """
#     读取一个人的只能回复内容的页面
#     :return:
#     """


def delete_a_auto_reply_setting(user_info, keywords_id):
    """
    完全删除一条回复
    :return:
    """
    keywords_info = BaseModel.fetch_by_id(Keywords, keywords_id)
    keywords_info.delete()
    GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = True
    return SUCCESS


def create_a_auto_reply_setting(user_info, chatroom_list, message_list, keyword_list, keywords_id = None):
    """
    update_material 指是否读取每个material中的id。如果为True，则用老的。如果为False，则用新的
    新建一条回复setting
    :return:
    """
    if keywords_id is not None:
        keywords_info = BaseModel.fetch_by_id(Keywords, keywords_id)
        if not keywords_info:
            return ERR_WRONG_ITEM
    else:
        keywords_info = CM(Keywords)

    now_time = datetime_to_timestamp_utc_8(datetime.now())
    keywords_info.client_id = user_info.client_id
    keywords_info.welcome = 0
    keywords_info.create_time = now_time
    keywords_info.status = 1

    chatroomname_list = list()
    for chatroomname in chatroom_list:
        chatroomname_list.append(chatroomname)

    reply_content_list = list()
    for i, message_info in enumerate(message_list):
        reply_content = dict()
        send_type = message_info.get("send_type")
        text = message_info.get("text")
        reply_content['type'] = send_type
        reply_content['content'] = text
        reply_content['seq'] = i
        reply_content_list.append(reply_content)

    keyword_dict = dict()
    for i, keyword_info in enumerate(keyword_list):
        precise = list()
        fuzzy = list()
        is_full_match = keyword_info.get("is_full_match")
        keyword = keyword_info.get("keyword_content")
        if keyword:
            if is_full_match:
                precise.append(keyword)
            else:
                fuzzy.append(keyword)
        else:
            logger.error("没有读取到关键词")
            continue
        keyword_dict['precise'] = precise
        keyword_dict['fuzzy'] = fuzzy

    keywords_info.keywords = keyword_dict
    keywords_info.reply_content = reply_content_list
    keywords_info.chatroom_list = chatroomname_list
    keywords_info.save()

    GLOBAL_RULES_UPDATE_FLAG[GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG] = True
    return SUCCESS


def activate_rule_and_add_task_to_consumption_task(ar_setting_id, message_chatroomname, message_said_username):
    ar_setting_info = db.session.query(AutoReplySettingInfo).filter(
        AutoReplySettingInfo.setting_id == ar_setting_id).first()
    if not ar_setting_info:
        return ERR_WRONG_ITEM

    valid_chatroom_list = []
    uqr_info = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == ar_setting_info.user_id,
                                                          UserQunRelateInfo.chatroomname == message_chatroomname). \
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
