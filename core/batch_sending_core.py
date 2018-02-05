# -*- coding: utf-8 -*-
from copy import deepcopy
import logging

from sqlalchemy import func

from configs.config import db, ERR_WRONG_ITEM, SUCCESS
from core.qun_manage_core import get_a_chatroom_dict_by_uqun_id
from models.batch_sending_models import BatchSendingTaskInfo, BatchSendingTaskTargetRelate, \
    BatchSendingTaskMaterialRelate
from models.material_library_models import UserMaterialLibrary
from models.production_consumption_models import ConsumptionTaskStream

logger = logging.getLogger('main')


def get_batch_sending_task(user_info):
    """
    根据一个人，把所有的这个人可见的群发任务都出来
    :param user_info:
    :return:
    """
    bs_task_info_list = db.session.query(BatchSendingTaskInfo).filter(
        BatchSendingTaskInfo.user_id == user_info.user_id).all()
    result = []
    for bs_task_info in bs_task_info_list:
        status, task_detail_res = get_task_detail(bs_task_info=bs_task_info)
        if status == SUCCESS:
            result.append(deepcopy(task_detail_res))
        else:
            pass

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
    res.setdefault("task_create_time", bs_task_info.task_create_time)

    temp_tsc = db.session.query(func.count(ConsumptionTaskStream.task_id)). \
        filter(ConsumptionTaskStream.task_type == 1,
               ConsumptionTaskStream.task_relevant_id == bs_task_info.sending_task_id).all()
    # FIXME-zwf 这里的格式还需要调整
    res.setdefault("task_sended_count", temp_tsc)

    # TODO-zwf 想办法把失败的读出来
    res.setdefault("task_sended_failed_count", 0)

    # 生成群信息
    res.setdefault("chatroom_list", [])
    bs_task_target_list = db.session.query(BatchSendingTaskTargetRelate).filter(
        BatchSendingTaskTargetRelate.uqun_id).all()
    if not bs_task_target_list:
        return ERR_WRONG_ITEM
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
        BatchSendingTaskMaterialRelate).order_by(
        BatchSendingTaskMaterialRelate.send_seq).all()
    if not bs_task_material_list:
        return ERR_WRONG_ITEM
    material_id_list = []
    for bs_task_material_relate in bs_task_material_list:
        material_id_list.append(bs_task_material_relate.material_id)
    for material_id in material_id_list:
        temp_material_dict = dict()
        um_lib = db.session.query(UserMaterialLibrary).filter(UserMaterialLibrary.material_id == material_id).first()
        temp_material_dict.setdefault("material_id", um_lib.material_id)
        temp_material_dict.setdefault("task_send_type", um_lib.task_send_type)
        temp_material_dict.setdefault("task_send_content", {})
        temp_content = um_lib.task_send_content
        if um_lib.task_send_type == 1:
            text = temp_content.get("text")
            if text is None:
                logger.warning(u"解析material中content失败. material_id: %s." % material_id)
                text = ""
            else:
                pass
            temp_material_dict['task_send_content'].setdefault("text", text)
        else:
            logger.critical("NotImplementedError: 暂不考虑其他类型.")
            raise NotImplementedError
        res["message_list"].append(deepcopy(temp_material_dict))

    return SUCCESS, res


def get_task_fail_detail(sending_task_id):
    """
    读取一个任务的任务情况，成功或者失败
    :param sending_task_id:
    :return:
    """


def create_a_sending_task():
    """
    将前端发送过来的任务放入task表，并将任务放入consumption_task
    :return:
    """


def _add_task_to_consumption_task():
    """
    将任务放入consumption_task
    :return:
    """
