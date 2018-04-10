# -*- coding: utf-8 -*-
import logging
import time

from copy import deepcopy
from datetime import datetime
from sqlalchemy import desc

from configs.config import db, SUCCESS, WARN_HAS_DEFAULT_QUN, ERR_WRONG_USER_ITEM, ERR_WRONG_ITEM, \
    ERR_RENAME_OR_DELETE_DEFAULT_GROUP, MSG_TYPE_SYS, ERR_HAVE_SAME_PEOPLE, USER_CHATROOM_R_PERMISSION_1, UserQunR
from core_v2.wechat_core import WechatConn
from models.qun_friend_models import GroupInfo
from models_v2.base_model import BaseModel, CM
from utils.u_email import EmailAlert
from utils.u_time import datetime_to_timestamp_utc_8
from utils.u_transformat import str_to_unicode

logger = logging.getLogger('main')


# 因为之前的表关系废掉了，所以现在需要重新写
#


def set_default_group(client_id):
    """
    设置未分组的群的组
    :param client_id:
    :return:
    """
    count_uqr = BaseModel.count(UserQunR, where_clause = BaseModel.where_dict({"client_id": client_id}))
    # 如果已经有了默认群，则不去建立默认群
    if count_uqr > 0:
        logger.warning(u"已有默认分组. user_id: %s." % client_id)
        return WARN_HAS_DEFAULT_QUN
    else:
        group_info = _create_new_group(u"未分组", is_default = True)
        group_list = list()
        group_list.append(group_info)
        uqr = CM(UserQunR)
        uqr.client_id = client_id
        uqr.group_list = group_list
        uqr.save()
        logger.debug(u"已建立默认分组. user_id: %s." % client_id)
        return SUCCESS


def create_new_group(group_name, client_id):
    uqr = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": client_id}))
    if not uqr:
        set_default_group(client_id)
        uqr = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": client_id}))
    else:
        group_name_exist = [group_info.keys[0] for group_info in uqr.group_list]
        if group_name in group_name_exist:
            return ERR_WRONG_ITEM, None

    group_info = _create_new_group(group_name)
    uqr.group_list.append(group_info)

    temp_dict = dict()
    temp_dict.setdefault("group_id", group_name)
    temp_dict.setdefault("group_nickname", group_name)
    temp_dict.setdefault("is_default", True if group_name == u'未分组' else False)
    temp_dict.setdefault("chatroom_list", [])
    logger.info(u"添加分组. user_id: %s. group_name: %s." % (client_id, group_name))
    return SUCCESS, temp_dict


def get_group_list(user_info):
    uqr = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    group_list = uqr.group_list
    if not group_list:
        logger.error(u"无默认分组. user_id: %s." % user_info.client_id)
        return ERR_WRONG_ITEM, None

    res = []
    for group_info in group_list:
        temp_dict = dict()
        temp_dict.setdefault("group_id", group_info.get("group_name"))
        temp_dict.setdefault("group_nickname", group_info.get("group_name"))
        temp_dict.setdefault("is_default", group_info.get("is_default"))
        temp_dict.setdefault("create_time", group_info.get("create_time"))
        temp_dict.setdefault("update_time", group_info.get("update_time"))
        temp_dict.setdefault("chatroom_list", group_info.get("chatroom_list"))

        res.append(deepcopy(temp_dict))
    logger.info(u"获取分组列表. user_id: %s." % user_info.client_id)
    return SUCCESS, res


# def get_chatroom_list_by_user_info(user_info):
#     uqr_info_list = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == user_info.user_id).all()
#     chartoom_list = []
#     for uqr_info in uqr_info_list:
#         status, chatroom_dict = get_a_chatroom_dict_by_uqun_id(uqr_info=uqr_info)
#         if status == SUCCESS:
#             chartoom_list.append(chatroom_dict)
#     return SUCCESS, chartoom_list


def rename_a_group(group_rename, group_id, client_id):
    uqr = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": client_id}))
    group_list = uqr.group_list
    for group_info in group_list:
        if group_info.get("group_name") == group_id:
            if group_info.get("is_default") == 1:
                logger.error(u"默认分组无法更名. group_id: %s. user_id: %s." % (group_id, client_id))
                return ERR_RENAME_OR_DELETE_DEFAULT_GROUP
            group_info.set("group_name", group_rename)
            logger.info(u"重命名成功. group_id: %s." % group_id)
            return SUCCESS
    logger.error(u"无法找到该分组. group_id: %s." % group_id)
    return ERR_WRONG_ITEM


def delete_a_group(group_id, client_id):
    uqr = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": client_id}))
    group_list = uqr.group_list
    group_info_default = None
    group_info_deleted = None
    group_info_deleted_i = -1
    for i, group_info in enumerate(group_list):
        if group_info.get("group_name") == group_id:
            group_info_deleted = group_info
            group_info_deleted_i = i
        if group_info.get("is_default") == 1:
            group_info_default = group_info

    if group_info_default is None:
        logger.error(u"无法找到该默认分组. client_id: %s." % client_id)
        return ERR_WRONG_ITEM
    if group_info_deleted is None or group_info_deleted_i == -1:
        logger.error(u"无法找到该分组. group_id: %s." % group_id)
        return ERR_WRONG_ITEM
    if group_info_deleted.get("is_default") == 1:
        logger.error(u"默认分组无法删除. group_id: %s. user_id: %s." % (group_id, client_id))
        return ERR_RENAME_OR_DELETE_DEFAULT_GROUP
    chatroom_list = group_info_deleted.get("chatroom_list")
    for chatroom in chatroom_list:
        if chatroom not in group_info_default.chatroom_list:
            group_info_default.chatroom_list.append(chatroom)
    group_list.pop(group_info_deleted_i)
    logger.info(u"已删除分组. old_group_id: %s. user_id: %s." % (group_id, client_id))
    return SUCCESS


def transfer_qun_into_a_group(old_group_id, new_group_id, chatroomname, client_id):
    uqr = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": client_id}))
    group_list = uqr.group_list
    group_info_old = None
    group_info_new = None
    for i, group_info in enumerate(group_list):
        if group_info.get("group_name") == old_group_id:
            group_info_old = group_info
            continue
        if group_info.get("group_name") == new_group_id:
            group_info_new = group_info
            continue
    if group_info_old is None or group_info_new is None:
        logger.error(u"无法找到该分组. group_id: %s." % new_group_id)
        return ERR_WRONG_ITEM

    if chatroomname not in group_info_old.get("chatroom_list"):
        logger.error(u"无法找到该群. group_id: %s. chatroomname: %s." % (new_group_id, chatroomname))
        return ERR_WRONG_ITEM

    group_info_old.get("chatroom_list").remove(chatroomname)
    group_info_new.get("chatroom_list").append(chatroomname)

    logger.info(u"转移分组成功. new_group_id: %s. chatroomname: %s." % (new_group_id, chatroomname))
    return SUCCESS


def check_whether_message_is_add_qun(a_message):
    """
    根据一条Message，返回是否为加群，如果是，则完成加群动作
    :return:
    """
    is_add_qun = False
    msg_type = a_message.type
    content = str_to_unicode(a_message.content)

    if msg_type == MSG_TYPE_SYS and content.find(u'邀请你') != -1:
        is_add_qun = True
        bot_username = a_message.username
        user_nickname = content.split(u'邀请')[0][1:-1]
        logger.info(u"发现加群. user_nickname: %s. chatroomname: %s." % (user_nickname, a_message.talker))
        status, user_info = _bind_qun_success(a_message.talker, user_nickname, bot_username)
        we_conn = WechatConn()
        if status == SUCCESS:
            we_conn.send_txt_to_follower("恭喜！友问币答小助手已经进入您的群了，可立即使用啦\n想再次试用？再次把我拉进群就好啦", user_info.open_id)
        else:
            EmailAlert.send_ue_alert(u"有用户尝试绑定机器人，但未绑定成功.疑似网络通信问题. "
                                     u"user_nickname: %s." % user_nickname)
    return is_add_qun


def _bind_qun_success(chatroomname, user_nickname, bot_username):
    """
    当确认message为加群时，将群加入到系统中
    :param user_nickname: 除了有可能是nickname，还有可能是displayname
    :return:
    """

    # 因为AMember等库更新未必在Message之前（在网速较慢的情况下可能出现）
    # 所以此处先sleep一段时间，等待AMember更新后再读取
    time.sleep(5)

    # 标记是否找到member_flag
    a_member_list = db.session.query(AMember).filter(AMember.chatroomname == chatroomname,
                                                     AMember.displayname == user_nickname,
                                                     AMember.is_deleted == 0).all()
    if len(a_member_list) > 1:
        logger.error(u"一个群中出现两个相同的群备注名，无法确定身份. chatroomname: %s. user_nickname: %s." %
                     (chatroomname, user_nickname))
        return ERR_HAVE_SAME_PEOPLE, None
    elif len(a_member_list) == 0:
        member_flag = False
    else:
        member_flag = True

    # 标记是否找到user_info
    user_info_list = db.session.query(UserInfo).filter(UserInfo.nick_name == user_nickname).all()
    if len(user_info_list) > 1:
        logger.error(u"根据nickname无法确定其身份. user_nickname: %s." % user_nickname)
        return ERR_HAVE_SAME_PEOPLE, None
    elif len(user_info_list) == 0:
        user_info_flag = False
    else:
        user_info_flag = True

    if member_flag is True and user_info_flag is True:
        logger.error(u"同时匹配到群备注和用户昵称，无法识别用户身份. chatroomname: %s. user_nickname: %s." %
                     (chatroomname, user_nickname))
        return ERR_HAVE_SAME_PEOPLE, None
    elif member_flag is False and user_info_flag is False:
        logger.error(u"没有找到群备注也没有找到用户昵称.没有找到该用户. chatroomname: %s. user_nickname: %s." %
                     (chatroomname, user_nickname))
        return ERR_WRONG_USER_ITEM, None
    elif user_info_flag is True:
        user_info = user_info_list[0]
    else:
        user_info = db.session.query(UserInfo).filter(UserInfo.username == a_member_list[0].username).first()
        if not user_info:
            logger.error(u"没有找到对应的用户信息. user_username: %s." % a_member_list[0].username)
            return ERR_WRONG_ITEM, None

    user_id = user_info.user_id

    bot_info = db.session.query(BotInfo).filter(BotInfo.username == bot_username).first()
    if not bot_info:
        logger.error(u"bot信息出错. bot_username: %s" % bot_username)
        return ERR_WRONG_ITEM, None

    bot_id = bot_info.bot_id

    ubr_info_list = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_id,
                                                               UserBotRelateInfo.bot_id == bot_id).all()
    if len(ubr_info_list) > 1:
        logger.error(u"找到多个bot关系. user_id: %s." % user_id)
        return ERR_WRONG_ITEM, None
    elif len(ubr_info_list) == 0:
        logger.error(u"没有找到bot关系. user_id: %s." % user_id)
        return ERR_WRONG_ITEM, None
    else:
        ubr_info = ubr_info_list[0]

    user_bot_rid = ubr_info.user_bot_rid

    group_info_list = db.session.query(GroupInfo).filter(GroupInfo.user_id == user_id, GroupInfo.is_default == 1).all()
    if len(group_info_list) > 1:
        logger.error(u"发现多个默认分组. user_nickname: %s." % user_nickname)
        return ERR_WRONG_ITEM, None
    elif len(group_info_list) == 0:
        logger.error(u"无默认分组. user_nickname: %s." % user_nickname)
        return ERR_WRONG_ITEM, None
    else:
        group_info = group_info_list[0]

    # 检查该群是否已经被记录过
    exist_uqr_info = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == user_id,
                                                                UserQunRelateInfo.chatroomname == chatroomname).first()
    # 该群被记录过
    if exist_uqr_info:
        exist_uqbr_info = db.session.query(UserQunBotRelateInfo).filter(
            UserQunBotRelateInfo.uqun_id == exist_uqr_info.uqun_id,
            UserQunBotRelateInfo.user_bot_rid == user_bot_rid).first()
        if exist_uqbr_info:
            if exist_uqbr_info.is_error:
                exist_uqbr_info.is_error = False
                db.session.merge(exist_uqbr_info)
                db.session.commit()
                logger.info("将已经有过的群激活. uqbr_id: %s." % exist_uqbr_info.rid)
            else:
                logger.warning(u"机器人未出错，但却重新进群，逻辑可能有误. uqbr_rid: %s." % exist_uqbr_info.rid)
        else:
            logger.error(u"有uqr但却没有uqbr，关系出错. uqun_id: %s." % exist_uqr_info.uqun_id)
            return ERR_WRONG_ITEM, None
    else:
        uqr_info = UserQunRelateInfo()
        uqr_info.user_id = user_id
        uqr_info.chatroomname = chatroomname
        uqr_info.group_id = group_info.group_id
        uqr_info.create_time = datetime.now()
        uqr_info.is_deleted = False

        db.session.add(uqr_info)
        db.session.commit()
        logger.debug(u"user与群关系已绑定. uqun_id: %s." % uqr_info.uqun_id)

        uqbr_info = UserQunBotRelateInfo()
        uqbr_info.uqun_id = uqr_info.uqun_id
        uqbr_info.user_bot_rid = ubr_info.user_bot_rid
        uqbr_info.is_error = False

        db.session.add(uqbr_info)
        db.session.commit()
        logger.info(u"绑定群的四个关系. uqbr_id: %s." % uqbr_info.rid)
        # generate_welcome_message_c_task_into_new_qun(uqr_info, user_id, bot_info.username)

    return SUCCESS, user_info


def check_is_removed(a_message):
    """
    根据一条Message，返回是否为被移除群聊，如果是，则完成相关动作
    :return:
    """

    is_removed = False
    msg_type = a_message.type
    content = str_to_unicode(a_message.content)
    if msg_type == MSG_TYPE_SYS and content.find(u'移出群聊') != -1:
        is_removed = True
        bot_username = a_message.username
        chatroomname = a_message.talker
        logger.info(u"发现机器人被踢出群聊. bot_username: %s. chatroomname: %s." % (bot_username, chatroomname))
        _remove_bot_process(bot_username, chatroomname)
    return is_removed


def _remove_bot_process(bot_username, chatroomname):
    bot_info = db.session.query(BotInfo).filter(BotInfo.username == bot_username).first()
    if not bot_info:
        logger.error(u"没有找到bot信息. bot_id: %s." % bot_info.bot_id)
    bot_id = bot_info.bot_id
    uqr_info_list = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.chatroomname == chatroomname).all()
    ubr_info_list = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.bot_id == bot_id).all()

    for ubr_info in ubr_info_list:
        user_bot_rid = ubr_info.user_bot_rid
        for uqr_info in uqr_info_list:
            uqun_id = uqr_info.uqun_id

            uqbr_info = db.session.query(UserQunBotRelateInfo). \
                filter(UserQunBotRelateInfo.uqun_id == uqun_id,
                       UserQunBotRelateInfo.user_bot_rid == user_bot_rid).first()
            if not uqbr_info:
                continue
            uqbr_info.is_error = True
            db.session.merge(uqbr_info)
    filter_list_bcr = BotChatroomR.get_filter_list(chatroomname = chatroomname, username = bot_username, is_on = True)
    bot_chatroom_r_list = db.session.query(BotChatroomR).filter(*filter_list_bcr).all()
    # 理论上只有一个
    for bcr in bot_chatroom_r_list:
        bcr.is_on = False

    db.session.commit()
    logger.info(u"已将该bot所有相关群设置为异常")
    return SUCCESS


def get_a_chatroom_dict_by_uqun_id(uqr_info=None, uqun_id=None):
    if not uqr_info and not uqun_id:
        raise ValueError(u"传入参数有误，不能传入空参数")

    if uqun_id:
        uqr_info = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.uqun_id == uqun_id).first()

    if not uqr_info:
        logger.error(u"无法通过uqun_id找到群关系. uqun_id: %s." % uqun_id)
        return ERR_WRONG_ITEM, None

    temp_chatroom_dict = dict()
    temp_chatroom_dict.setdefault("chatroom_id", uqr_info.uqun_id)
    a_contact = db.session.query(AContact).filter(AContact.username == uqr_info.chatroomname).first()
    if not a_contact:
        logger.warning(u"群信息不在AContact中，uqr_info.chatroomname: %s" % str(uqr_info.chatroomname))
        temp_chatroom_dict.setdefault("chatroom_nickname", 0)
        temp_chatroom_dict.setdefault("chatroom_member_count", 0)
        temp_chatroom_dict.setdefault("chatroom_avatar", "")
        temp_chatroom_dict.setdefault("chatroom_status", -2)
    else:
        if a_contact.nickname is None or a_contact.nickname == "":
            a_chatroom = db.session.query(AChatroom).filter(AChatroom.chatroomname == uqr_info.chatroomname).first()
            displayname = str_to_unicode(a_chatroom.displayname)
            if len(displayname) > 16:
                displayname = displayname[0:16]
            temp_chatroom_dict.setdefault("chatroom_nickname", displayname)
        else:
            temp_chatroom_dict.setdefault("chatroom_nickname", a_contact.nickname)

        temp_chatroom_dict.setdefault("chatroom_member_count", a_contact.member_count)
        temp_chatroom_dict.setdefault("chatroom_avatar", a_contact.avatar_url2)

        if uqr_info.is_deleted is True:
            temp_chatroom_dict.setdefault("chatroom_status", -1)
        else:
            ubr_info_list = db.session.query(UserBotRelateInfo).filter(
                UserBotRelateInfo.user_id == uqr_info.user_id).all()
            if not ubr_info_list:
                logger.error(u"没有对应的机器人关系可以使用. 逻辑错误. user_id: %s." % uqr_info.user_id)
                return ERR_WRONG_USER_ITEM, None
            status_is_error_flag = True
            for ubr_info in ubr_info_list:
                uqbr_info = db.session.query(UserQunBotRelateInfo).filter(
                    UserQunBotRelateInfo.uqun_id == uqr_info.uqun_id,
                    UserQunBotRelateInfo.user_bot_rid == ubr_info.user_bot_rid).first()
                if not uqbr_info:
                    logger.error(
                        u"没有对应的uqbr关系. uqun_id: %s. user_bot_rid: %s." % (uqr_info.uqun_id, ubr_info.user_bot_rid))
                    return ERR_WRONG_USER_ITEM, None
                if not uqbr_info.is_error:
                    status_is_error_flag = False
                    break
            if status_is_error_flag is True:
                temp_chatroom_dict.setdefault("chatroom_status", -3)
            else:
                temp_chatroom_dict.setdefault("chatroom_status", 0)

    return SUCCESS, temp_chatroom_dict


def _create_new_group(group_name, is_default=False):
    now_time = datetime_to_timestamp_utc_8(datetime.now())

    group_info = dict()
    group_info["group_name"] = group_name
    group_info["is_default"] = is_default
    group_info["create_time"] = now_time
    group_info["create_time"] = now_time
    group_info["chatroom_list"] = list()

    return group_info
