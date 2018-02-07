# -*- coding: utf-8 -*-
import json
from copy import deepcopy
import logging

from datetime import datetime
from sqlalchemy import func, desc

from configs.config import db, ERR_WRONG_ITEM, SUCCESS, ERR_WRONG_USER_ITEM, CONSUMPTION_TASK_TYPE
from core.qun_manage_core import get_a_chatroom_dict_by_uqun_id
from models.android_db_models import AContact
from models.batch_sending_models import BatchSendingTaskInfo, BatchSendingTaskTargetRelate, \
    BatchSendingTaskMaterialRelate
from models.material_library_models import UserMaterialLibrary
from models.production_consumption_models import ConsumptionTaskStream, ConsumptionTask
from models.qun_friend_models import UserQunRelateInfo, UserQunBotRelateInfo
from models.user_bot_models import UserBotRelateInfo, BotInfo
from utils.u_time import datetime_to_timestamp_utc_8

logger = logging.getLogger('main')


def get_batch_sending_task(user_info):
    """
    根据一个人，把所有的这个人可见的群发任务都出来
    :param user_info:
    :return:
    """
    bs_task_info_list = db.session.query(BatchSendingTaskInfo).filter(
        BatchSendingTaskInfo.user_id == user_info.user_id).order_by(
        desc(BatchSendingTaskInfo.task_create_time)).all()
    result = []
    for bs_task_info in bs_task_info_list:
        status, task_detail_res = get_task_detail(bs_task_info=bs_task_info)
        if status == SUCCESS:
            result.append(deepcopy(task_detail_res))
        else:
            logger.error(u"部分任务无法读取. sending_task_id: %s." % bs_task_info.sending_task_id)

    return SUCCESS, result


def get_task_detail(sending_task_id=None, bs_task_info=None):
    """
    读取一个任务的所有信息
    """
    if not sending_task_id and not bs_task_info:
        raise ValueError(u"传入参数有误，不能传入空参数")

    if sending_task_id:
        bs_task_info = db.session.query(BatchSendingTaskInfo).filter(
            BatchSendingTaskInfo.sending_task_id == sending_task_id).first()

    if not bs_task_info:
        return ERR_WRONG_ITEM, None

    res = dict()
    res.setdefault("sending_task_id", sending_task_id)
    res.setdefault("task_covering_chatroom_count", bs_task_info.task_covering_qun_count)
    res.setdefault("task_covering_people_count", bs_task_info.task_covering_people_count)
    res.setdefault("task_create_time", datetime_to_timestamp_utc_8(bs_task_info.task_create_time))

    temp_tsc = db.session.query(func.count(ConsumptionTaskStream.chatroomname)). \
        filter(ConsumptionTaskStream.task_type == 1,
               ConsumptionTaskStream.task_relevant_id == bs_task_info.sending_task_id).all()

    res.setdefault("task_sended_count", temp_tsc[0][0])

    # TODO-zwf 想办法把失败的读出来
    res.setdefault("task_sended_failed_count", 0)

    # 生成群信息
    res.setdefault("chatroom_list", [])
    bs_task_target_list = db.session.query(BatchSendingTaskTargetRelate).filter(
        BatchSendingTaskTargetRelate.sending_task_id == bs_task_info.sending_task_id).all()
    if not bs_task_target_list:
        return ERR_WRONG_ITEM, None
    uqun_id_list = []
    for bs_task_target in bs_task_target_list:
        uqun_id_list.append(bs_task_target.uqun_id)
    for uqun_id in uqun_id_list:
        status, tcd_res = get_a_chatroom_dict_by_uqun_id(uqun_id=uqun_id)
        if status == SUCCESS:
            res['chatroom_list'].append(deepcopy(tcd_res))
        else:
            pass

    # 生成material信息
    res.setdefault("message_list", [])
    bs_task_material_list = db.session.query(BatchSendingTaskMaterialRelate).filter(
        BatchSendingTaskMaterialRelate.sending_task_id == bs_task_info.sending_task_id).order_by(
        BatchSendingTaskMaterialRelate.send_seq).all()
    if not bs_task_material_list:
        return ERR_WRONG_ITEM, None
    material_id_list = []
    for bs_task_material_relate in bs_task_material_list:
        material_id_list.append(bs_task_material_relate.material_id)
    for material_id in material_id_list:
        temp_material_dict = dict()
        um_lib = db.session.query(UserMaterialLibrary).filter(UserMaterialLibrary.material_id == material_id).first()
        temp_material_dict.setdefault("material_id", um_lib.material_id)
        temp_material_dict.setdefault("task_send_type", um_lib.task_send_type)
        temp_content = json.loads(um_lib.task_send_content)
        if um_lib.task_send_type == 1:
            text = temp_content.get("text")
            if text is None:
                logger.warning(u"解析material中content失败. material_id: %s." % material_id)
                text = ""
            else:
                pass
            temp_material_dict.setdefault("text", text)
        else:
            logger.critical(u"NotImplementedError: 暂不考虑其他类型.")
            raise NotImplementedError
        res["message_list"].append(deepcopy(temp_material_dict))

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
        um_lib = UserMaterialLibrary()
        um_lib.user_id = user_info.user_id
        send_type = message_info.get("send_type")
        if send_type == 1:
            um_lib.task_send_type = send_type
            text = message_info.get("text")
            if not text:
                logger.error("没有读取到文字")
                continue
            um_lib.task_send_content = json.dumps({"text": text})
        else:
            logger.warning("目前只允许1类任务")
            continue
        um_lib.used_count = 1
        um_lib.create_time = now_time
        um_lib.last_used_time = now_time
        db.session.add(um_lib)
        db.session.commit()

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
    if not isinstance(uqr_info, UserQunRelateInfo):
        raise TypeError
    if not isinstance(um_lib, UserMaterialLibrary):
        raise TypeError
    if not isinstance(bs_task_info, BatchSendingTaskInfo):
        raise TypeError

    c_task = ConsumptionTask()
    c_task.qun_owner_user_id = uqr_info.user_id
    c_task.task_initiate_user_id = bs_task_info.user_id
    c_task.chatroomname = uqr_info.chatroomname
    c_task.task_type = CONSUMPTION_TASK_TYPE["batch_sending_task"]
    c_task.task_relevant_id = bs_task_info.sending_task_id

    c_task.task_send_type = um_lib.task_send_type
    c_task.task_send_content = um_lib.task_send_content

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
