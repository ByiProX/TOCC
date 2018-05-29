# -*- coding: utf-8 -*-
import json
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
from core_v2.send_msg import send_ws_to_android
from core_v2.wechat_core import WechatConn, wechat_conn_dict
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
    # uqr_list = BaseModel.fetch_all(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    uqr_list = BaseModel.fetch_all(UserQunR, "*",
                                   where_clause = BaseModel.and_(
                                       ["=", "client_id", user_info.client_id],
                                       ["=", "status", 1])
                                   )
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
    chatroom_dict['chatroom_nickname'] = chatroom.nickname_real
    if chatroom.nickname_real == "":
        chatroom_dict['chatroom_nickname'] = chatroom.nickname_default
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
        uqr.group_id = unicode(client_id) + u'_0'
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

    # add by quentin
    try:
        chatroom_nickname_real = BaseModel.fetch_one("a_chatroom", "*",
                                                     where_clause=BaseModel.and_(
                                                         ["=", "chatroomname", a_message.talker]
                                                     )).nickname_real
        if not chatroom_nickname_real:
            chatroom_nickname_real = u"您新建的群"
    except Exception:
        chatroom_nickname_real = u"您新建的群"

    ###################
    if msg_type == MSG_TYPE_ENTERCHATROOM and content.find(u'邀请你') != -1:
        is_add_qun = True
        status, invitor_username, user_nickname = extract_enter_chatroom_msg(content)
        if status == SUCCESS:
            bot_username = a_message.bot_username
            logger.info(u"发现加群. user_nickname: %s. chatroomname: %s. invitor_username: %s." % (user_nickname, a_message.talker, invitor_username))
            status, user_info_list = _bind_qun_success(a_message.talker, user_nickname, bot_username, invitor_username)
            if not user_info_list:
                return is_add_qun
            for user_info in user_info_list:
                we_conn = wechat_conn_dict.get(user_info.app)

                if we_conn is None:
                    logger.info(u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (user_info.app, json.dumps(wechat_conn_dict.keys())))
                if status == SUCCESS:
                    # add by quentin
                    client_qun_info = BaseModel.fetch_one("client", "*",
                                                          where_clause=BaseModel.where_dict(
                                                              {"client_id": user_info.client_id}
                                                          ))

                    if client_qun_info.qun_count == 1 and client_qun_info.qun_count >= client_qun_info.qun_used:
                        info_data = {
                            "task": "send_message",
                            "to": user_info.username,
                            "type": 1,
                            "content": u"恭喜！ 友问币答小助手已经进入%s了，可立即使用啦。\n在群里发 btc 试试？"
                                       % chatroom_nickname_real
                        }

                        try:
                            status = send_ws_to_android(bot_username, info_data)
                            if status == SUCCESS:
                                logger.info(u"首次入群---通知任务发送成功, client_id: %s." % user_info.client_id)
                            else:
                                logger.info(u"首次入群---通知任务发送失败, client_id: %s." % user_info.client_id)
                        except Exception:
                            pass

                    else:
                        info_data = {
                            "task": "send_message",
                            "to": user_info.username,
                            "type": 1,
                            "content": u"恭喜！友问币答小助手已经进入%s了。但目前处于试用阶段，请在30分钟内联系我们客服mm激活小助手哦。"
                                       % chatroom_nickname_real
                        }

                        try:
                            status = send_ws_to_android(bot_username, info_data)
                            if status == SUCCESS:
                                logger.info(u"非首次入群---通知任务发送成功, client_id: %s." % user_info.client_id)
                            else:
                                logger.info(u"非首次入群---通知任务发送失败, client_id: %s." % user_info.client_id)
                        except Exception:
                            pass

                    #########################
                else:
                    info_data = {
                        "task": "send_message",
                        "to": user_info.username,
                        "type": 1,
                        "content": u"抱歉！友问币答小助手进入%s失败，请尝试再次拉入。"
                                   % chatroom_nickname_real
                    }

                    try:
                        status = send_ws_to_android(bot_username, info_data)
                        if status == SUCCESS:
                            logger.info(u"入群失败---通知任务发送成功, client_id: %s." % user_info.client_id)
                        else:
                            logger.info(u"入群失败---通知任务发送失败, client_id: %s." % user_info.client_id)
                    except Exception:
                        pass
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

    user_info_list = BaseModel.fetch_all(UserInfo, "*", where_clause = BaseModel.where_dict({"username": member_username}))
    # user_info = BaseModel.fetch_one(UserInfo, "*", where_clause = BaseModel.where_dict({"username": member_username}))
    if not user_info_list:
        logger.error(u"找不到该用户. username: %s." % member_username)
        return ERR_WRONG_ITEM, None

    # user_id = user_info.user_id

    logger.info(u"已匹配到 " + unicode(len(user_info_list)) + u" 个 client")
    for user_info in user_info_list:
        ubr = BaseModel.fetch_one(UserBotR, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id, "bot_username": bot_username}))
        if not ubr:
            logger.info(u"非绑定当前账号机器人加群，可能是别的账号，莫慌， client_id: %s. bot_username: %s." % (user_info.client_id, bot_username))
            user_info_list.remove(user_info)
            continue
        logger.info(u"该用户绑定的机器人加群, client_id: %s. bot_username: %s." % (user_info.client_id, bot_username))
        bot_info = BaseModel.fetch_one(BotInfo, "*", where_clause = BaseModel.where_dict({"username": bot_username}))
        if not bot_info:
            logger.error(u"bot信息出错. bot_username: %s" % bot_username)
            return ERR_WRONG_ITEM, None

        uqr_exist = BaseModel.fetch_one(UserQunR, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                            "chatroomname": chatroomname}))
        # add by quentin
        # 统计当前群数量
        uqr_count = BaseModel.count(UserQunR,
                                    where_clause=BaseModel.where_dict(
                                        {"client_id": user_info.client_id}
                                    ))
        # ------------------------------------#

        if not uqr_exist:
            uqr = CM(UserQunR)
            uqr.client_id = user_info.client_id
            uqr.chatroomname = chatroomname
            uqr.status = 1
            uqr.group_id = unicode(user_info.client_id) + u"_0"
            uqr.create_time = int(time.time())
            uqr.is_paid = 0 if uqr_count > 0 else 1
            uqr.save()
            logger.info(u"user与群关系已绑定. user_id: %s. chatroomname: %s." % (user_info.client_id, chatroomname))
        else:
            # logger.warning(u"机器人未出错，但却重新进群，逻辑可能有误. chatroomname: %s." % chatroomname)
            # add by qunetin
            uqr_exist.client_id = user_info.client_id
            uqr_exist.chatroomname = chatroomname
            uqr_exist.status = 1
            uqr_exist.group_id = unicode(user_info.client_id) + u"_0"
            uqr_exist.create_time = int(time.time())
            uqr_exist.is_paid = 0
            uqr_exist.save()
            logger.warning(u"机器人未出错，但却重新进群，逻辑可能有误. chatroomname: %s." % chatroomname)

        # 修改机器人在群里的群备注
        modify_self_displayname(user_info.client_id, chatroomname, bot_username)

        # add by quentin ###################################
        # 更新client表中的qun_used数据
        client = BaseModel.fetch_one("client", "*",
                                     where_clause=BaseModel.and_(
                                         ["=", "client_id", user_info.client_id]
                                     ))

        qun_used_count = BaseModel.count("client_qun_r",
                                         where_clause=BaseModel.and_(
                                             ["=", "client_id", user_info.client_id],
                                             ["=", "status", 1]
                                         ))

        client.qun_used = qun_used_count
        client.save()
        ###############################################

    return SUCCESS, user_info_list


def modify_self_displayname(client_id, chatroomname, bot_username):
    logger.info(u"尝试修改机器人备注. client_id: %s. chatroomname: %s. bot_username: %s." % (client_id, chatroomname, bot_username))
    ubr = BaseModel.fetch_one(UserBotR, "*", where_clause = BaseModel.where_dict({"client_id": client_id}))

    if ubr and ubr.chatbot_default_nickname:
        data_json = dict()
        chatroomnick = ubr.chatbot_default_nickname
        data_json['selfdisplayname'] = chatroomnick
        data_json['chatroomname'] = chatroomname
        data_json['task'] = "update_self_displayname"
        send_ws_to_android(bot_username, data_json)


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
