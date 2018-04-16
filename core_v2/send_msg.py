# -*- coding: utf-8 -*-
import json
import logging

import requests

from configs.config import SUCCESS, ERR_UNKNOWN_ERROR, ANDROID_SERVER_URL_SEND_MASS_MESSAGE, \
    ANDROID_SERVER_URL_SEND_MESSAGE

logger = logging.getLogger('main')


def send_msg_to_android(bot_username, message_list, to_list):
    data = dict()
    data.setdefault("bot_username", bot_username)
    data.setdefault("message_list", message_list)
    data.setdefault("to_list", to_list)
    logger.info(u"安卓发送任务. data: %s." % json.dumps(data))
    url = ANDROID_SERVER_URL_SEND_MASS_MESSAGE
    logger.info(u"安卓发送任务. url: %s." % url)
    response = requests.post(url = url, json = data)
    response_json = json.loads(response.content)
    err_code = response_json.get("err_code")
    if err_code == 0:
        return SUCCESS
    else:
        logger.info(u"任务发送失败. bot_username: %s." % bot_username)
        return ERR_UNKNOWN_ERROR


def send_ws_to_android(bot_username, data):
    logger.info(u"send_ws_to_android. data: %s." % json.dumps(data))
    url = ANDROID_SERVER_URL_SEND_MESSAGE
    logger.info(u"send_ws_to_android. url: %s." % url)
    response = requests.post(url = url, json = {"bot_username": bot_username,
                                                "data": data})
    response_json = json.loads(response.content)
    err_code = response_json.get("err_code")
    if err_code == 0:
        return SUCCESS
    else:
        logger.info(u"send_ws_to_android failed. bot_username: %s." % bot_username)
        return ERR_UNKNOWN_ERROR
