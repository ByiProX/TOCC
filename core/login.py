# -*- coding: utf-8 -*-

import logging
import json

from datetime import datetime
from flask import request

from config import db, ERR_INVALID_PARAMS, SUCCESS
from core.wechat import WechatConn
from models.user_bot import UserInfo
from utils.u_response import make_response

logger = logging.getLogger('main')

wechat_conn = WechatConn()


def verify_code():
    data_json = json.loads(request.data)
    code = data_json.get('code')

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
        wechat = UserInfo.get_user_info(open_id, user_access_token, code)

    # Mark
    # 测试账号
    if wechat:
        if wechat.is_test:
            logger.info('is_test')
            logger.info('wechat_id: ' + str(wechat.id))
            wechat_neilzwh = db.session.query(UserInfo).filter(UserInfo.id == 16).first()
            wechat = wechat_neilzwh
        return make_response(SUCCESS, token=wechat.token)

    return make_response(ERR_INVALID_PARAMS)


def get_user_info(open_id, user_access_token, code):
    wechat = db.session.query(UserInfo).filter(UserInfo.open_id == open_id).first()
    wechat_utils = WechatConn()
    res_json = wechat_utils.get_user_info(open_id=open_id, user_access_token=user_access_token)

    if res_json.get('openid'):
        wechat_json = dict()
        wechat_json['open_id'] = res_json.get('openid')
        wechat_json['nick_name'] = res_json.get('nickname')
        wechat_json['sex'] = res_json.get('sex')
        wechat_json['province'] = res_json.get('province')
        wechat_json['city'] = res_json.get('city')
        wechat_json['country'] = res_json.get('country')
        wechat_json['avatar_url'] = res_json.get('headimgurl')
        wechat_json['unionid'] = res_json.get('unionid')
        wechat_json['last_login_time'] = datetime.now()
        wechat_json['code'] = code

        if wechat is None:
            wechat = UserInfo().load_from_json(wechat_json).generate_create_time().generate_token()
            # Mark
            # wechat.bot_id = 2
            db.session.add(wechat)
        else:
            wechat.load_from_json(wechat_json)
        db.session.commit()
