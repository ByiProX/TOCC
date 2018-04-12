# -*- coding: utf-8 -*-
import logging
from copy import deepcopy
from datetime import datetime

from sqlalchemy import func, desc

from configs.config import db, ERR_WRONG_ITEM, SUCCESS, ERR_WRONG_USER_ITEM, CONSUMPTION_TASK_TYPE, BatchSendTask, \
    Chatroom
from models_v2.base_model import BaseModel
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
            message_json["text"] = content.get("content")
            message_json["seq"] = content.get("seq")
            message_list.append(message_json)

        res["message_list"] = message_list
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
    batch_send_task = BaseModel.fetch_by_id(BatchSendTask, batch_send_task_id)
    if not batch_send_task:
        logger.error(u"群发不存在, batch_send_task_id: %s." + unicode(batch_send_task_id))
        return ERR_WRONG_ITEM, None

    # batch_send_task = BaseModel.fetch_one(BatchSendTask, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    res = dict()
    chatroom_list = batch_send_task.chatroom_list
    chatroom_count = len(chatroom_list)
    member_count = 0
    for chatroomname in chatroom_list:
        chatroom = BaseModel.fetch_one(Chatroom, "member_count",
                                       where_clause = BaseModel.where_dict({"chatroomname": chatroomname}))
        member_count += chatroom.member_count

    message_list = list()
    content_list = batch_send_task.content_list
    for content in content_list:
        message_json = dict()
        message_json["task_send_type"] = content.get("type")
        message_json["text"] = content.get("content")
        message_json["seq"] = content.get("seq")
        message_list.append(message_json)

    res["message_list"] = message_list
    res["task_covering_chatroom_count"] = chatroom_count
    res["task_covering_people_count"] = member_count
    res["task_create_time"] = batch_send_task.create_time
    # TODO: TBD
    res["task_sended_count"] = chatroom_count
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
    # 先验证各个群情况
    now_time = datetime.now()
    bs_task_info = BatchSendingTaskInfo()
    bs_task_info.user_id = user_info.user_id
    bs_task_info.task_covering_qun_count = 0
    bs_task_info.task_covering_people_count = 0
    bs_task_info.task_status = 1
    bs_task_info.task_status_content = "等待开始"
    bs_task_info.is_deleted = False
    bs_task_info.task_create_time = now_time
    db.session.add(bs_task_info)
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

        bs_task_target = BatchSendingTaskTargetRelate()
        bs_task_target.sending_task_id = bs_task_info.sending_task_id
        bs_task_target.uqun_id = uqun_id
        db.session.add(bs_task_target)
        valid_chatroom_list.append(uqr_info)
    db.session.commit()

    # 处理message，入库material
    valid_material_list = []
    for i, message_info in enumerate(message_list):
        message_return, um_lib = analysis_frontend_material_and_put_into_mysql(user_info.user_id, message_info,
                                                                               now_time, update_material=True)
        if message_return == SUCCESS:
            pass
        elif message_return == ERR_WRONG_ITEM:
            continue

        material_id = um_lib.material_id
        bs_task_material = BatchSendingTaskMaterialRelate()
        bs_task_material.material_id = material_id
        bs_task_material.sending_task_id = bs_task_info.sending_task_id
        bs_task_material.send_seq = i
        db.session.add(bs_task_material)
        valid_material_list.append(um_lib)
    db.session.commit()

    # 更新主库中的数量
    bs_task_info.task_covering_qun_count = task_covering_qun_count
    bs_task_info.task_covering_people_count = task_covering_people_count
    db.session.merge(bs_task_info)
    db.session.commit()

    # 确认任务放入无问题后，将任务发出
    for uqr_info_iter in valid_chatroom_list:
        for um_lib_iter in valid_material_list:
            _add_task_to_consumption_task(uqr_info_iter, um_lib_iter, bs_task_info)
    return SUCCESS


def _add_task_to_consumption_task(uqr_info, um_lib, bs_task_info):
    """
    将任务放入consumption_task
    :return:
    """
    status = add_task_to_consumption_task(uqr_info, um_lib, bs_task_info.user_id,
                                          CONSUMPTION_TASK_TYPE["batch_sending_task"], bs_task_info.sending_task_id)
    return status
