# -*- coding: utf-8 -*-
import logging
import time
import traceback

from copy import deepcopy
from datetime import datetime, timedelta
from xml.etree import ElementTree

from sqlalchemy import desc

from configs.config import db, SUCCESS, WARN_HAS_DEFAULT_QUN, ERR_WRONG_USER_ITEM, ERR_WRONG_ITEM, \
    ERR_RENAME_OR_DELETE_DEFAULT_GROUP, MSG_TYPE_SYS, ERR_HAVE_SAME_PEOPLE, USER_CHATROOM_R_PERMISSION_1, UserQunR, \
    UserGroupR, UserInfo, BotInfo, UserBotR, Chatroom, MSG_TYPE_ENTERCHATROOM, ERR_UNKNOWN_ERROR
from core_v2.wechat_core import WechatConn
from models.qun_friend_models import GroupInfo
from models_v2.base_model import BaseModel, CM
from utils.u_email import EmailAlert
from utils.u_time import datetime_to_timestamp_utc_8
from utils.u_transformat import str_to_unicode, unicode_to_str

logger = logging.getLogger('main')


# 因为之前的表关系废掉了，所以现在需要重新写
#


def create_new_group(group_name, client_id):
    ugr_last = BaseModel.fetch_one(UserGroupR, "group_id", where_clause = BaseModel.where_dict({"client_id": client_id}), order_by = BaseModel.order_by({"create_time": "DESC"}))
    if ugr_last:
        order = int(ugr_last.group_id.split(u"_")[1]) + 1
    else:
        order = 1
    # 默认分组的 group_id = client_id_0, 并不显式地存在库里
    group_id = unicode(client_id) + u"_" + unicode(order)

    ugr = CM(UserGroupR)
    ugr.group_id = group_id
    ugr.client_id = client_id
    ugr.group_name = group_name
    ugr.create_time = datetime_to_timestamp_utc_8(datetime.now())
    ugr.save()

    group_info = dict()
    group_info.setdefault("client_group_r_id", ugr.get_id())
    group_info.setdefault("group_id", group_id)
    group_info.setdefault("group_nickname", group_name)
    group_info.setdefault("is_default", 0)
    group_info.setdefault("chatroom_list", [])
    logger.info(u"添加分组. user_id: %s. group_name: %s." % (client_id, group_name))
    return SUCCESS, group_info


def get_group_list(user_info):
    ugr_list = BaseModel.fetch_all(UserGroupR, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))

    group_chatroom = dict()
    uqr_list = BaseModel.fetch_all(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    for uqr in uqr_list:
        group_chatroom.setdefault(uqr.group_id, list())
        group_chatroom[uqr.group_id].append(get_chatroom_dict(uqr.chatroomname))

    res = []
    # 默认分组的 group_id = client_id_0, 并不显式得存在库里
    res.append({"group_id": unicode(user_info.client_id) + u"_0",
                "group_nickname": u"未分组",
                "create_time": user_info.create_time,
                "is_default": 1,
                "chatroom_list": group_chatroom.get(unicode(user_info.client_id) + u"_0") or list()})

    for ugr in ugr_list:
        temp_dict = dict()
        temp_dict.setdefault("group_id", ugr.group_id)
        temp_dict.setdefault("group_nickname", ugr.group_name)
        temp_dict.setdefault("create_time", ugr.create_time)
        temp_dict.setdefault("is_default", 0)
        chatroom_list = group_chatroom.get(ugr.group_id) or list()
        temp_dict.setdefault("chatroom_list", chatroom_list)

        res.append(temp_dict)
    logger.info(u"获取分组列表. user_id: %s." % user_info.client_id)
    return SUCCESS, res


def get_chatroom_dict(chatroomname):
    chatroom = BaseModel.fetch_one(Chatroom, "*",
                                   where_clause = BaseModel.where_dict({"chatroomname": chatroomname}))
    chatroom_dict = dict()
    chatroom_dict['chatroom_id'] = chatroom.get_id()
    chatroom_dict['chatroom_nickname'] = chatroom.nickname
    chatroom_dict['chatroomname'] = chatroomname
    chatroom_dict['chatroom_member_count'] = chatroom.member_count
    chatroom_dict['avatar_url'] = chatroom.avatar_url
    chatroom_dict['chatroom_status'] = 0

    return chatroom_dict


def rename_a_group(group_rename, group_id, client_id):
    if group_id.endswith(u"_0"):
        logger.error(u"默认分组无法重命名. group_id: %s. user_id: %s." % (group_id, client_id))
        return ERR_RENAME_OR_DELETE_DEFAULT_GROUP
    ugr = BaseModel.fetch_one(UserGroupR, "*", where_clause = BaseModel.where_dict({"client_id": client_id, "group_id": group_id}))
    if not ugr:
        logger.error(u"无法找到该分组. group_id: %s." % group_id)
        return ERR_WRONG_ITEM
    ugr.group_name = group_rename
    ugr.update()
    logger.info(u"重命名成功. group_id: %s." % group_id)
    return SUCCESS


def delete_a_group(group_id, client_id):
    if group_id.endswith(u"_0"):
        logger.error(u"默认分组无法删除. group_id: %s. user_id: %s." % (group_id, client_id))
        return ERR_RENAME_OR_DELETE_DEFAULT_GROUP
    ugr = BaseModel.fetch_one(UserGroupR, "*", where_clause = BaseModel.where_dict({"client_id": client_id, "group_id": group_id}))
    if not ugr:
        logger.error(u"无法找到该分组. group_id: %s." % group_id)
        return ERR_WRONG_ITEM
    # ugr.group_name = group_rename
    ugr.delete()
    uqr_list = BaseModel.fetch_all(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": client_id, "group_id": group_id}))
    for uqr in uqr_list:
        uqr.group_id = u""
        uqr.save()

    logger.info(u"已删除分组. old_group_id: %s. user_id: %s." % (group_id, client_id))
    return SUCCESS


def transfer_qun_into_a_group(old_group_id, new_group_id, chatroomname, client_id):
    uqr = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": client_id,
                                                                                  "group_id": old_group_id,
                                                                                  "chatroomname": chatroomname}))
    if not uqr:
        logger.error(u"无法找到该群. group_id: %s. client_id: %s. chatroomname: %s." % (new_group_id, client_id, chatroomname))
        return ERR_WRONG_ITEM
    uqr.group_id = new_group_id
    uqr.save()

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

    if msg_type == MSG_TYPE_ENTERCHATROOM and content.find(u'邀请你') != -1:
        is_add_qun = True
        status, user_nickname, invitor_username = extract_enter_chatroom_msg(content)
        if status == SUCCESS:
            bot_username = a_message.bot_username
            logger.info(u"发现加群. user_nickname: %s. chatroomname: %s." % (user_nickname, a_message.talker))
            status, user_info = _bind_qun_success(a_message.talker, user_nickname, bot_username, invitor_username)
            we_conn = WechatConn()
            if status == SUCCESS:
                we_conn.send_txt_to_follower("恭喜！友问币答小助手已经进入您的群了，可立即使用啦\n想再次试用？再次把我拉进群就好啦", user_info.open_id)
            else:
                # EmailAlert.send_ue_alert(u"有用户尝试绑定机器人，但未绑定成功.疑似网络通信问题. "
                #                          u"user_nickname: %s." % user_nickname)
                pass
    return is_add_qun


def _bind_qun_success(chatroomname, user_nickname, bot_username, member_username):
    """
    当确认message为加群时，将群加入到系统中
    :param user_nickname: 除了有可能是nickname，还有可能是displayname
    :return:
    """

    # 因为AMember等库更新未必在Message之前（在网速较慢的情况下可能出现）
    # 所以此处先sleep一段时间，等待AMember更新后再读取

    # member_username = fetch_member_by_nickname(chatroomname, user_nickname)
    # if not member_username:
    #     logger.error(u"找不到该成员. nickname: %s." % user_nickname)
    #     return ERR_WRONG_ITEM, None

    user_info = BaseModel.fetch_one(UserInfo, "*", where_clause = BaseModel.where_dict({"username": member_username}))
    if not user_info:
        logger.error(u"找不到该用户. username: %s." % member_username)
        return ERR_WRONG_ITEM, None

    # user_id = user_info.user_id

    bot_info = BaseModel.fetch_one(BotInfo, "*", where_clause = BaseModel.where_dict({"username": bot_username}))
    if not bot_info:
        logger.error(u"bot信息出错. bot_username: %s" % bot_username)
        return ERR_WRONG_ITEM, None

    uqr_exist = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                        "chatroomname": chatroomname}))
    if not uqr_exist:
        uqr = CM(UserQunR)
        uqr.client_id = user_info.client_id
        uqr.chatroomname = chatroomname
        uqr.status = 1
        uqr.group_id = unicode(user_info.client_id) + u"_0"
        uqr.create_time = datetime_to_timestamp_utc_8(datetime.now())
        uqr.save()
        logger.info(u"user与群关系已绑定. user_id: %s. chatroomname: %s." % (user_info.client_id, chatroomname))
    else:
        logger.warning(u"机器人未出错，但却重新进群，逻辑可能有误. chatroomname: %s." % chatroomname)

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
        bot_username = a_message.bot_username
        chatroomname = a_message.talker
        logger.info(u"发现机器人被踢出群聊. bot_username: %s. chatroomname: %s." % (bot_username, chatroomname))
        _remove_bot_process(bot_username, chatroomname)
    return is_removed


def _remove_bot_process(bot_username, chatroomname):
    ubr_list = BaseModel.fetch_all(UserBotR, "*", where_clause = BaseModel.where_dict({"bot_username": bot_username}))
    for ubr in ubr_list:
        uqr_list = BaseModel.fetch_all(UserQunR, "*", where_clause = BaseModel.where_dict({"chatroomname": chatroomname,
                                                                                           "client_id": ubr.client_id}))
        for uqr in uqr_list:
            uqr.status = 0
            uqr.update()
    logger.info(u"已将该bot所有相关群设置为异常")
    return SUCCESS


def extract_enter_chatroom_msg(content):
    content = content.split(u":\n")[1].replace("\t", "").replace("\n", "")
    invitor_username = None
    invitor_nickname = None
    content = unicode_to_str(content)
    try:
        etree_msg = ElementTree.fromstring(content)
        etree_link_list = etree_msg.iter(tag = "link")
        for etree_link in etree_link_list:
            print etree_link.get("name")
            name = etree_link.get("name")
            if name == "username":
                etree_member_list = etree_link.find("memberlist")
                for member in etree_member_list:
                    for attr in member:
                        if attr.tag == "username":
                            invitor_username = attr.text
                        elif attr.tag == "nickname":
                            invitor_nickname = attr.text
        return SUCCESS, invitor_username, invitor_nickname
    except Exception as e:
        logger.error("邀请进群解析失败")
        logger.error(traceback.format_exc())
        return ERR_UNKNOWN_ERROR, None, None


if __name__ == '__main__':
    # content = '<sysmsg type="sysmsgtemplate"> <sysmsgtemplate> <content_template type="tmpl_type_profile"> <plain><![CDATA[]]></plain> <template><![CDATA["$username$"邀请"$names$"加入了群聊]]></template> <link_list> <link name="username" type="link_profile"> <memberlist> <member> <username><![CDATA[wxid_zy8gemkhx2r222]]></username> <nickname><![CDATA[ZYunH]]></nickname> </member> </memberlist> </link> <link name="names" type="link_profile"> <memberlist> <member> <username><![CDATA[wxid_56mqtj11ewa022]]></username> <nickname><![CDATA[呆呆球]]></nickname> </member> </memberlist> <separator><![CDATA[、]]></separator> </link> </link_list> </content_template> </sysmsgtemplate> </sysmsg>'
    # print extract_enter_chatroom_msg(content)
    pass
