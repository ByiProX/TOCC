# -*- coding: utf-8 -*-

"""
ws的建立、释放、检测
以及将任务发送给各个安卓
"""
import json

from configs.config import WS_MAP, TASK_SEND_TYPE, db
import logging

from models.android_db_models import AFriend, AChatroomR
from models.production_consumption_models import ConsumptionTask

logger = logging.getLogger('main')


def send_task_content_to_ws(bot_username, target_username, task_send_type, content):
    # TODO-zc WebsocketModel
    ws = WS_MAP.get(bot_username)
    if ws:
        text_json = dict()
        text_json['username'] = target_username
        text_json['content'] = content
        text_json['type'] = task_send_type
        text = json.dumps(text_json)
        print 'text', text
        ws.send(text)
    else:
        logger.error(u"websocket error, username: " + bot_username)
    # """
    # 将文字发给ws
    # {
    #       "material_id": 1,
    #       "task_send_type": 1,
    #       "task_send_content": {
    #         "text": "这是一段发送的文字。这段文字不能太长，但是预计可以在500字以内"
    #       }
    #     },
    #     {
    #       "material_id": 1,
    #       "task_send_type": 2,
    #       "task_send_content": {
    #         "title": "一个美丽的图片或者什么的",
    #         "description": "一张图片的描述",
    #         "url": "http:"
    #       }
    #     }
    # 发送内容的类型；1为文字；2为公众号；3为链接；4为文件；5为小程序
    # """
    #
    # task_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    # qun_owner_user_id = db.Column(db.BigInteger, index=True, nullable=False)
    # task_initiate_user_id = db.Column(db.BigInteger, index=True, nullable=False)
    # chatroomname = db.Column(db.String(32), index=True, nullable=False)
    #
    # # 1为群发消息；2为自动回复；3为回复签到；4为入群回复
    # task_type = db.Column(db.Integer, index=True, nullable=False)
    #
    # # 发送内容的类型；1为文字；2为公众号；3为链接；4为文件；5为小程序
    # task_send_type = db.Column(db.Integer, index=True, nullable=False)
    # task_send_content = db.Column(db.String(2048), index=True, nullable=False)
    # bot_username = db.Column(db.String(32), index=True, nullable=False)
    #
    # message_received_time = db.Column(db.DateTime, index=True, nullable=False)
    # task_create_time = db.Column(db.DateTime, index=True, nullable=False)


def update_chatroom_members_info(chatroomname):
    a_chatroom_r_list = db.session.query(AChatroomR).filter(AChatroomR.chatroomname == chatroomname).all()
    for a_chatroom_r in a_chatroom_r_list:
        bot_username = a_chatroom_r.username
        ws = WS_MAP.get(bot_username)
        if ws:
            update_chatroom_members_info_core(bot_username = bot_username, chatroomname = chatroomname)
            break


def update_chatroom_members_info_core(bot_username, chatroomname):
    ws = WS_MAP.get(bot_username)
    if ws:
        text_json = dict()
        text_json['chatroomname'] = chatroomname
        text_json['type'] = TASK_SEND_TYPE['update_chatroom_members_info']
        text = json.dumps(text_json)
        print 'text', text
        ws.send(text)
    else:
        logger.error(u"websocket error, username: " + bot_username)


def update_members_info(member_usernames):
    a_friend_list = db.session.query(AFriend).filter(AFriend.to_username.in_(member_usernames.split(';'))).all()
    for a_friend in a_friend_list:
        bot_username = a_friend.from_username
        ws = WS_MAP.get(bot_username)
        if ws:
            update_members_info_core(bot_username = bot_username, member_usernames = member_usernames)
            break


def update_members_info_core(bot_username, member_usernames):
    ws = WS_MAP.get(bot_username)
    if ws:
        text_json = dict()
        text_json['member_usernames'] = member_usernames
        text_json['type'] = TASK_SEND_TYPE['update_members_info']
        text = json.dumps(text_json)
        print 'text', text
        ws.send(text)
    else:
        logger.error(u"websocket error, username: " + bot_username)
