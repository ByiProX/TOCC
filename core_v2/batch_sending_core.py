# -*- coding: utf-8 -*-
import logging
from copy import deepcopy
from datetime import datetime

from sqlalchemy import func, desc

from configs.config import db, ERR_WRONG_ITEM, SUCCESS, ERR_WRONG_USER_ITEM, CONSUMPTION_TASK_TYPE, BatchSendTask, \
    Chatroom, BATCH_SEND_TASK_STATUS_1
from models_v2.base_model import BaseModel, CM
from utils.u_time import datetime_to_timestamp_utc_8

logger = logging.getLogger('main')


def get_batch_sending_task(user_info, task_per_page, page_number):
    """
    根据一个人，把所有的这个人可见的群发任务都出来
    :param user_info:
    :return:
    """
    result = []
    batch_send_task_list = BaseModel.fetch_all(BatchSendTask, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    for batch_send_task in batch_send_task_list:
        res = dict()
        chatroom_list = batch_send_task.chatroom_list
        chatroom_count = len(chatroom_list)
        member_count = 0
        for chatroomname in chatroom_list:
            chatroom = BaseModel.fetch_one(Chatroom, "member_count", where_clause = BaseModel.where_dict({"chatroomname": chatroomname}))
            member_count += chatroom.member_count

        message_list = list()
        content_list = batch_send_task.content_list
        for content in content_list:
            message_json = dict()
            message_json["task_send_type"] = content.get("type")
            message_json["text"] = content.get("text")
            message_json["seq"] = content.get("seq")
            message_list.append(message_json)

        res["message_list"] = message_list
        res["chatroom_list"] = chatroom_list
        res["task_covering_chatroom_count"] = chatroom_count
        res["task_covering_people_count"] = member_count
        res["task_create_time"] = batch_send_task.create_time
        # TODO: TBD
        res["task_sended_count"] = chatroom_count
        res["task_sended_failed_count"] = 0
        result.append(res)

    return SUCCESS, result


def get_task_detail(batch_send_task_id):
    """
    读取一个任务的所有信息
    """
    # batch_send_task = BaseModel.fetch_one(BatchSendTask, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    batch_send_task = BaseModel.fetch_by_id(BatchSendTask, batch_send_task_id)
    if not batch_send_task:
        logger.error(u"群发不存在, batch_send_task_id: %s." + unicode(batch_send_task_id))
        return ERR_WRONG_ITEM, None

    res = dict()
    chatroom_list = batch_send_task.chatroom_list


    message_list = list()
    content_list = batch_send_task.content_list
    for content in content_list:
        message_json = dict()
        message_json["task_send_type"] = content.get("type")
        message_json["text"] = content.get("content")
        message_json["seq"] = content.get("seq")
        message_list.append(message_json)

    res["message_list"] = message_list
    res["task_covering_chatroom_count"] = batch_send_task.chatroom_count
    res["task_covering_people_count"] = batch_send_task.people_count
    res["task_create_time"] = batch_send_task.create_time
    # TODO: TBD
    res["task_sended_count"] = batch_send_task.chatroom_count
    res["task_sended_failed_count"] = 0

    return SUCCESS, res


def get_task_fail_detail(sending_task_id):
    """
    读取一个任务的任务情况，成功或者失败
    :param sending_task_id:
    :return:
    """


def create_a_sending_task(user_info, chatroom_list, message_list):
    """
    将前端发送过来的任务放入task表，并将任务放入consumption_task
    :return:
    """

    chatroom_count = len(chatroom_list)
    member_count = 0
    for chatroomname in chatroom_list:
        chatroom = BaseModel.fetch_one(Chatroom, "member_count",
                                       where_clause = BaseModel.where_dict({"chatroomname": chatroomname}))
        if not chatroom:
            logger.error(u"未获取到 chatroom, chatroomname: %s." % chatroomname)
            continue
        member_count += chatroom.member_count

    if chatroom_count == 0 or member_count == 0:
        logger.error(u"没有发送对象, 批量发送任务创建失败")
        return ERR_WRONG_ITEM

    now_time = datetime_to_timestamp_utc_8(datetime.now())
    batch_send_task = CM(BatchSendTask)
    batch_send_task.client_id = user_info.client_id
    batch_send_task.chatroom_list = chatroom_list
    batch_send_task.chatroom_count = chatroom_count
    batch_send_task.people_count = member_count
    batch_send_task.is_deleted = 0
    batch_send_task.create_time = now_time
    batch_send_task.status = BATCH_SEND_TASK_STATUS_1
    batch_send_task.status_content = ""
    content_list = list()
    for i, message in enumerate(message_list):
        message_dict = dict()
        message_dict["type"] = message.get("send_type")
        message_dict["text"] = message.get("text")
        message_dict["seq"] = i
        content_list.append(message_dict)

    batch_send_task.content_list = content_list

    batch_send_task.save()
    # TODO: Send Task
    print u'send task'
    return SUCCESS


def _add_task_to_consumption_task(uqr_info, um_lib, bs_task_info):
    """
    将任务放入consumption_task
    :return:
    """
    status = add_task_to_consumption_task(uqr_info, um_lib, bs_task_info.user_id,
                                          CONSUMPTION_TASK_TYPE["batch_sending_task"], bs_task_info.sending_task_id)
    return status
