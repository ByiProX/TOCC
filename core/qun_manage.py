# -*- coding: utf-8 -*-
import logging

from copy import deepcopy
from datetime import datetime

from config import db, SUCCESS, WARN_HAS_DEFAULT_QUN, ERR_WRONG_USER_ITEM, ERR_WRONG_ITEM
from models.android_db import AContact
from models.qun_friend import GroupInfo, UserQunRelateInfo
from models.user_bot import UserInfo

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
        GroupInfo.create_time).all()

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
    group_info = db.session.query(GroupInfo.group_id == group_id).first()
    if not group_info:
        return ERR_WRONG_ITEM
    if group_info.user_id != user_id:
        return ERR_WRONG_USER_ITEM
    group_info.group_nickname = group_rename
    db.session.commit()
    return SUCCESS


def delete_a_group(group_id, user_id):
    group_info = db.session.query(GroupInfo.group_id == group_id).first()
    if not group_info:
        raise ERR_WRONG_ITEM
    if group_info.user_id != user_id:
        return ERR_WRONG_USER_ITEM
    if not group_info.is_owner:
        return ERR_WRONG_USER_ITEM

    user_default_group_info = db.session.query(GroupInfo.user_id == user_id, GroupInfo.is_default == 1).first()
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


def _create_new_group(user_id, group_name, is_default_group=False):
    group_info = GroupInfo()
    group_info.group_nickname = group_name
    group_info.user_id = user_id
    group_info.create_time = datetime.now()
    group_info.is_default = is_default_group
    db.session.add(group_info)
    db.session.commit()
