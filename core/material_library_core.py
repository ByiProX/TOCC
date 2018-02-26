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
    elif um_lib.task_send_type == TASK_SEND_TYPE['picture']:
        logger.critical(u"NotImplementedError: 暂不考虑其他类型.")
        raise NotImplementedError
        # title = temp_content.get("title")
        # if not title:
        #     title = ""
        # description = temp_content.get("description")
        # if not description:
        #     description = ""
        # url = temp_content.get("url")
        # if not url:
        #     logger.error(u"发现无地址的图片类型. material_id: %s." % material_id)
        #     url = ""
        # temp_material_dict.setdefault("title", title)
        # temp_material_dict.setdefault("description", description)
        # temp_material_dict.setdefault("url", url)
    else:
        logger.critical(u"NotImplementedError: 暂不考虑其他类型.")
        raise NotImplementedError
    return temp_material_dict


def analysis_frontend_material_and_put_into_mysql(user_id, message_info, now_time):
    # 确认是否为已有的资源
    material_id = message_info.get("material_id")
    if material_id:
        um_lib_old = db.session.query(UserMaterialLibrary).filter(
            UserMaterialLibrary.material_id == material_id).first()
        if not um_lib_old:
            logger.error(u"没有根据material_id找到对应的资源. material_id: %s." % material_id)
            return ERR_WRONG_ITEM, None

        um_lib_old.used_count += 1
        um_lib_old.last_used_time = now_time
        db.session.commit()
        return SUCCESS, um_lib_old

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
    elif send_type == TASK_SEND_TYPE['picture']:
        logger.warning("目前只允许文字任务")
        return ERR_WRONG_ITEM, None
        # title = message_info.get("title")
        # if not title:
        #     title = u""
        # description = message_info.get("description")
        # if not description:
        #     description = u""
        # media_id = message_info.get("server_id")
        # if not media_id:
        #     logger.error("没有读取到图片id")
        #     return ERR_WRONG_ITEM, None
        # status, url = _execute_media_id_and_update_cdn(media_id)
        # if status != SUCCESS:
        #     logger.error("无法正确获得url地址")
        #     return ERR_WRONG_ITEM, None
        # um_lib.task_send_content = json.dumps({"title": title,
        #                                        "description": description,
        #                                        "url": url})
    else:
        logger.warning("目前只允许文字和图片任务")
        return ERR_WRONG_ITEM, None
    um_lib.used_count = 1
    um_lib.create_time = now_time
    um_lib.last_used_time = now_time
    db.session.add(um_lib)
    db.session.commit()
    return SUCCESS, um_lib


def _execute_media_id_and_update_cdn(media_id):
    """
    根据media_id从微信端获取图片，并进行查重，上传到cdn，最终返回url
    :param media_id:
    :return:
    """
    status, media_file = _get_media_from_wechat(media_id)
    if status != SUCCESS:
        return status, None
    status, material_id = _check_media_whether_in_cdn(media_file)
    if status is True:
        um_lib = db.session.query(UserMaterialLibrary).filter(UserMaterialLibrary.material_id == material_id).first()
        if not um_lib:
            logger.error(u"没有读取到媒体id. material_id: %s." % material_id)
            return ERR_WRONG_ITEM, None
        temp_content = json.loads(um_lib.task_send_content)
        url = temp_content.get("url")
        if not url:
            logger.error(u"um_lib中没有找到对应的内容. material_id: %s." % material_id)
            return ERR_WRONG_ITEM, None
        return SUCCESS, url
    else:
        status, url = _upload_new_media_into_cdn(media_file)
        if status == SUCCESS:
            return SUCCESS, url
        else:
            return status, None


def _get_media_from_wechat(media_id):
    """
    从微信端得到相关的文件
    :param media_id:
    :return:
    """
    meida_file = ""
    return SUCCESS, meida_file


def _check_media_whether_in_cdn(media_file):
    """
    确定该文件是否需要再次上传cdn
    :param media_file:
    :return:
    """
    return False, 90


def _upload_new_media_into_cdn(media_file):
    """
    将已经确认过的新的媒体传入cdn
    :param media_file:
    :return:
    """
    url = "http:"
    return SUCCESS, url
