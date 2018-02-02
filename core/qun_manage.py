# -*- coding: utf-8 -*-
import logging

from copy import deepcopy
from datetime import datetime
from sqlalchemy import desc

from configs.config import db, SUCCESS, WARN_HAS_DEFAULT_QUN, ERR_WRONG_USER_ITEM, ERR_WRONG_ITEM, \
    ERR_RENAME_OR_DELETE_DEFAULT_GROUP, MSG_TYPE_SYS
from models.android_db import AContact
from models.qun_friend import GroupInfo, UserQunRelateInfo
from models.user_bot import UserInfo
from utils.u_str_unicode import str_to_unicode

logger = logging.getLogger('main')


# 因为之前的表关系废掉了，所以现在需要重新写
#


def set_default_group(user_info):
    """
    设置未分组的群的组
    :param user_info:
    :return:
    """
    if isinstance(user_info, UserInfo):
        pass
    cur = db.session.query(GroupInfo).filter(GroupInfo.user_id == UserInfo.user_id,
                                             GroupInfo.is_default == 1).first()
    # 如果已经有了默认群，则不去建立默认群
    if cur:
        return WARN_HAS_DEFAULT_QUN
    else:
        _create_new_group(user_info.user_id, "未分组", is_default_group=True)
        return SUCCESS


def create_new_group(group_name, token=None, user_id=None, user_info=None):
    if user_id:
        pass
    else:
        if token:
            user_info = db.session.query(UserInfo.token == UserInfo.token).first()
            user_id = user_info.user_id
        else:
            if user_info:
                user_id = user_info.user_id

    _create_new_group(user_id, group_name)
    return SUCCESS


def get_group_list(user_info):
    group_list = db.session.query(GroupInfo).filter(GroupInfo.user_id == user_info.user_id).order_by(
        desc(GroupInfo.create_time)).all()

    if not group_list:
        return ERR_WRONG_ITEM, None

    res = []
    for group_info in group_list:
        temp_dict = dict()
        temp_group_id = group_info.group_id
        temp_dict.setdefault("group_id", temp_group_id)
        temp_dict.setdefault("group_nickname", group_info.group_nickname)
        temp_dict.setdefault("chatroom_list", [])

        uqr_list = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.group_id == temp_group_id,
                                                              UserQunRelateInfo.is_deleted == 0).all()
        for uqr_info in uqr_list:
            temp_chatroom_dict = dict()
            a_contact = db.session.query(AContact).filter(AContact.username == uqr_info.chatroomname).first()
            if not a_contact:
                return ERR_WRONG_ITEM, None

            temp_chatroom_dict.setdefault("chatroom_id", uqr_info.uqun_id)

            temp_chatroom_dict.setdefault("chatroom_nickname", a_contact.nickname)

            temp_chatroom_dict.setdefault("chatroom_member_count", a_contact.member_count)

            if uqr_info.is_deleted is True:
                temp_chatroom_dict.setdefault("chatroom_status", -1)
            else:
                temp_chatroom_dict.setdefault("chatroom_status", 0)

            temp_chatroom_dict.setdefault("chatroom_avatar", a_contact.avatar_url2)

            temp_dict['chatroom_list'].append(deepcopy(temp_chatroom_dict))

        res.append(deepcopy(temp_dict))

    return SUCCESS, res


def rename_a_group(group_rename, group_id, user_id):
    group_info = db.session.query(GroupInfo).filter(GroupInfo.group_id == group_id).first()
    if not group_info:
        return ERR_WRONG_ITEM
    if group_info.user_id != user_id:
        return ERR_WRONG_USER_ITEM
    if group_info.is_default is True:
        return ERR_RENAME_OR_DELETE_DEFAULT_GROUP
    group_info.group_nickname = group_rename
    db.session.commit()
    return SUCCESS


def delete_a_group(group_id, user_id):
    group_info = db.session.query(GroupInfo).filter(GroupInfo.group_id == group_id).first()
    if not group_info:
        return ERR_WRONG_ITEM
    if group_info.user_id != user_id:
        return ERR_WRONG_USER_ITEM
    if group_info.is_default is True:
        return ERR_RENAME_OR_DELETE_DEFAULT_GROUP

    user_default_group_info = db.session.query(GroupInfo).filter(GroupInfo.user_id == user_id,
                                                                 GroupInfo.is_default == 1).first()

    if not user_default_group_info:
        return ERR_WRONG_ITEM
    user_default_group_id = user_default_group_info.group_id

    uqun_info_list = db.session.query(UserQunRelateInfo.group_id == group_id).all()
    for uqun_info in uqun_info_list:
        uqun_info.group_id = user_default_group_id
        db.session.merge(uqun_info)
    db.session.delete(group_info)
    db.session.commit()

    return SUCCESS


def transfor_qun_into_a_group(group_id, uqun_id, user_id):
    qun_info = db.session.query(UserQunRelateInfo.uqun_id == uqun_id).first()
    if not qun_info:
        return ERR_WRONG_ITEM
    if qun_info.user_id != user_id:
        return ERR_WRONG_USER_ITEM

    group_info = db.session.query(GroupInfo.group_id == group_id).first()
    if not group_info:
        raise ERR_WRONG_ITEM
    if group_info.user_id != user_id:
        return ERR_WRONG_USER_ITEM
    if not group_info.is_owner:
        return ERR_WRONG_USER_ITEM

    qun_info.group_id = group_id
    db.session.merge(qun_info)
    db.session.commit()

    return SUCCESS


def check_whether_message_is_add_qun(message_analysis):
    """
    根据一条Message，返回是否为加群，如果是，则完成加群动作
    :return:
    """
    is_add_qun = False
    msg_type = message_analysis.type
    content = str_to_unicode(message_analysis.content)

    if msg_type == MSG_TYPE_SYS and content.find(u'邀请你') != -1:
        is_add_qun = True

    return is_add_qun


def check_is_removed(message_analysis):
    """
    根据一条Message，返回是否为被移除群聊，如果是，则完成相关动作
    :return:
    """
    # content.find(u'移除群聊') != -1:


def _create_new_group(user_id, group_name, is_default_group=False):
    group_info = GroupInfo()
    group_info.group_nickname = group_name
    group_info.user_id = user_id
    group_info.create_time = datetime.now()
    group_info.is_default = is_default_group
    db.session.add(group_info)
    db.session.commit()
