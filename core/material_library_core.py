# -*- coding: utf-8 -*-
import json
import logging

from configs.config import db, ERR_WRONG_ITEM, SUCCESS, TASK_SEND_TYPE
from models.material_library_models import UserMaterialLibrary

logger = logging.getLogger('main')


def generate_material_into_frontend_by_material_id(material_id):
    temp_material_dict = dict()
    um_lib = db.session.query(UserMaterialLibrary).filter(
        UserMaterialLibrary.material_id == material_id).first()
    temp_material_dict.setdefault("material_id", um_lib.material_id)
    temp_material_dict.setdefault("task_send_type", um_lib.task_send_type)
    temp_content = json.loads(um_lib.task_send_content)
    if um_lib.task_send_type == TASK_SEND_TYPE['text']:
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
    return temp_material_dict


def analysis_frontend_material_and_put_into_mysql(user_id, message_info, now_time):
    um_lib = UserMaterialLibrary()
    um_lib.user_id = user_id
    send_type = message_info.get("send_type")
    if send_type == TASK_SEND_TYPE['text']:
        um_lib.task_send_type = send_type
        text = message_info.get("text")
        if not text:
            logger.error("没有读取到文字")
            return ERR_WRONG_ITEM, None
        um_lib.task_send_content = json.dumps({"text": text})
    else:
        logger.warning("目前只允许1类任务")
        return ERR_WRONG_ITEM, None
    um_lib.used_count = 1
    um_lib.create_time = now_time
    um_lib.last_used_time = now_time
    db.session.add(um_lib)
    db.session.commit()
    return SUCCESS, um_lib
