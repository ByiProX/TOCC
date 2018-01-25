# -*- coding: utf-8 -*-

import logging

from datetime import datetime

from config import db, ERR_INVALID_PARAMS, SUCCESS
from core.wechat import WechatConn
from models.user_bot import UserInfo
from utils.u_response import make_response

logger = logging.getLogger('main')

wechat_conn = WechatConn()


def verify_code(code):
    # if code == '111' or code == 111:
    #     return make_response(SUCCESS, token = 'O9URN0WKBHMB92K1ADBEIFTBJEJM')  # 磊
    # elif code == '222' or code == 222:
    #     return make_response(SUCCESS, token = 'O9URN0-B9FU7UKPHEHQYM278R0DI')  # 文浩

    # 用 code 获取 open_id
    res_json = wechat_conn.get_open_id_by_code(code=code)
    open_id = res_json.get('openid')
    user_access_token = res_json.get('access_token')

    if open_id is None:
        wechat_by_code = db.session.query(UserInfo).filter(UserInfo.code == code).first()
        if wechat_by_code is None:
            return make_response(ERR_INVALID_PARAMS)
        else:
            wechat = wechat_by_code
    else:
        wechat = get_user_info(open_id, user_access_token)

    if wechat:
        return make_response(SUCCESS, token=wechat.token)

    return make_response(ERR_INVALID_PARAMS)


def get_user_info(open_id, user_access_token):
    wechat = db.session.query(UserInfo).filter(UserInfo.open_id == open_id).first()
    if wechat is None:
        # TODO 新微信号，需要注册，分配机器人的内容
        wechat = UserInfo()
        wechat.create_time = datetime.now()
        db.session.add(wechat)

    wechat_utils = WechatConn()
    res_json = wechat_utils.get_user_info(open_id=open_id, user_access_token=user_access_token)

    if res_json.get('openid'):
        wechat.open_id = res_json.get('openid')
        wechat.nick_name = res_json.get('nick_name')
        wechat.sex = res_json.get('sex')
        wechat.province = res_json.get('province')
        wechat.city = res_json.get('city')
        wechat.country = res_json.get('country')
        wechat.avatar_url = res_json.get('avatar_url')
        wechat.union_id = res_json.get('unionid')
        wechat.code = res_json.get('code')
        wechat.last_login_time = datetime.now()

    db.session.commit()
    return wechat
