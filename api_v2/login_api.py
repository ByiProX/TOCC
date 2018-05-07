# -*- coding: utf-8 -*-
import base64
import json
import random

import cStringIO
import qrcode
import requests
from send_msg import send_ws_to_android
from models_v2.base_model import BaseModel

from flask import request

from configs.config import main_api_v2, ERR_PARAM_SET, ERR_INVALID_PARAMS, SUCCESS, INFO_NO_USED_BOT, \
    ERR_SET_LENGTH_WRONG, SIGN_DICT, ERR_ALREADY_LOGIN, APP_INFO_DICT
from core_v2.user_core import UserLogin, cal_user_basic_page_info, add_a_pre_relate_user_bot_info, get_bot_qr_code, \
    set_bot_name
from core_v2.wechat_core import wechat_conn_dict
from utils.u_model_json_str import verify_json
from utils.u_response import make_response

import logging

logger = logging.getLogger('main')


@main_api_v2.route('/verify_code', methods=['POST'])
def login_verify_code():
    verify_json()
    """
    用于验证
    code: 微信传入的code
    {"code":"111"}
    """
    if not request.data:
        return make_response(ERR_PARAM_SET)
    data_json = json.loads(request.data)
    code = data_json.get('code')
    app_name = data_json.get('app_name')
    if not code or not app_name:
        return make_response(ERR_INVALID_PARAMS)

    user_login = UserLogin(code, app_name)
    status, user_info = user_login.get_user_token()
    # TODO 这里有bug by frank5433
    if status == SUCCESS:
        return make_response(status, user_info=user_info.to_json_full())
    else:
        return make_response(status)


@main_api_v2.route("/get_user_info", methods=['POST'])
def app_get_user_info():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    return make_response(SUCCESS, user_info=user_info.to_json_full())


@main_api_v2.route('/get_user_basic_info', methods=['POST'])
def app_get_user_basic_info():
    """
    读取用户管理界面的所有的信息
    {"token":"test_token_123"}
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    status, res = cal_user_basic_page_info(user_info)

    if status == SUCCESS:
        return make_response(status, bot_info=res['bot_info'], user_func=res['user_func'], total_info=res['total_info'])
    # 目前INFO均返回为SUCCESS
    elif status == INFO_NO_USED_BOT:
        return make_response(SUCCESS, bot_info=res['bot_info'], user_func=res['user_func'],
                             total_info=res['total_info'])
    else:
        return make_response(status)


@main_api_v2.route('/initial_robot_nickname', methods=['POST'])
def app_initial_robot_nickname():
    """
    用于设置robot名字,并返回二维码
    {"token":"test_token_123","bot_nickname":"测试呀测试"}
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    bot_nickname = request.json.get('bot_nickname')
    if not bot_nickname:
        return make_response(ERR_INVALID_PARAMS)
    if len(bot_nickname) < 1 or len(bot_nickname) > 16:
        return make_response(ERR_SET_LENGTH_WRONG)

    status, ubr_info = add_a_pre_relate_user_bot_info(user_info, bot_nickname)

    if status != SUCCESS:
        return make_response(status)

    status, res = get_bot_qr_code(user_info)
    if status == SUCCESS:
        return make_response(status, qr_code=res)
    else:
        return make_response(status)


@main_api_v2.route("/get_bot_qr_code", methods=["POST"])
def app_get_bot_qr_code():
    """
    提供前端一个二维码
    :return:
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    status, res = get_bot_qr_code(user_info)

    if status == SUCCESS:
        return make_response(status, qr_code=res)
    else:
        return make_response(status)


@main_api_v2.route("/binded_wechat_bot", methods=["POST"])
def app_binded_wechat_bot():
    """
    当捆绑bot成功时，我应该得到的消息
    :return:
    """
    pass


# 进群只能通过Message，


@main_api_v2.route("/get_pc_login_qr", methods=['POST'])
def get_pc_login_qr():
    verify_json()
    app_name = request.json.get('app_name')
    if not app_name:
        return make_response(ERR_INVALID_PARAMS)
    sign = ""
    while sign is "" or sign in SIGN_DICT:
        for i in range(6):
            sign += chr(random.randint(65, 90))

    SIGN_DICT.setdefault(sign, None)
    app_info = APP_INFO_DICT[app_name]
    url_ori = app_info.get("URL_ORI").format(sign)
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(url_ori)
    qr.make()
    img = qr.make_image()
    buffer = cStringIO.StringIO()
    img.save(buffer, format="JPEG")
    b64qr = base64.b64encode(buffer.getvalue())

    return make_response(SUCCESS, qr=b64qr, sign=sign)


@main_api_v2.route("/pc_login", methods=['POST'])
def pc_login():
    verify_json()
    sign = request.json.get("sign")
    code = request.json.get("code")
    app_name = request.json.get('app_name')
    if not app_name or not sign or not code:
        return make_response(ERR_INVALID_PARAMS)

    if sign is None or sign not in SIGN_DICT or code is None:
        return make_response(ERR_INVALID_PARAMS)

    user_login = UserLogin(code, app_name)
    status, user_info = user_login.get_user_token()

    if status == SUCCESS:
        SIGN_DICT[sign] = user_info.token
    return make_response(status)


@main_api_v2.route("/verify_pc_login_qr", methods=['POST'])
def verify_pc_login_qr():
    verify_json()
    sign = request.json.get("sign")

    if sign is None or sign not in SIGN_DICT:
        return make_response(ERR_INVALID_PARAMS)

    if SIGN_DICT[sign] is False:
        return make_response(ERR_ALREADY_LOGIN)

    if SIGN_DICT[sign]:
        token = SIGN_DICT[sign]
        SIGN_DICT[sign] = False
        return make_response(SUCCESS, token=token, is_login=True)

    return make_response(SUCCESS, is_login=False)


# add by Quentin below
@main_api_v2.route("/get_signature", methods=['POST'])
def get_signature():
    verify_json()
    url = request.json.get("url")

    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    if url is None:
        return make_response(ERR_INVALID_PARAMS)
    try:
        we_conn = wechat_conn_dict.get(user_info.app)
        if we_conn is None:
            logger.info(
                u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (user_info.app, json.dumps(wechat_conn_dict.keys())))
        timestamp, noncestr, signature = we_conn.get_signature_from_access_token(url)
        return make_response(SUCCESS, timestamp=timestamp, noncestr=noncestr, signature=signature)
    except Exception as e:
        logger.error('ERROR  %s' % e)
        return make_response(ERR_INVALID_PARAMS)


@main_api_v2.route("/make_pic_2_qr", methods=['POST'])
def make_pic_2_qr():
    verify_json()
    pic_url = request.json.get('url')

    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(pic_url)
    qr.make()
    img = qr.make_image()
    buffer = cStringIO.StringIO()
    img.save(buffer, format="PNG")
    b64qr = base64.b64encode(buffer.getvalue())

    return make_response(SUCCESS, qr=b64qr)


@main_api_v2.route('/set_robot_nickname', methods=['POST'])
def app_set_robot_nickname():
    """
    用于设置rebot名字
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    bot_id = request.json.get('bot_id')
    if not bot_id:
        return make_response(ERR_INVALID_PARAMS)

    bot_nickname = request.json.get('bot_nickname')
    if not bot_nickname:
        return make_response(ERR_INVALID_PARAMS)
    if len(bot_nickname) < 1 or len(bot_nickname) > 16:
        return make_response(ERR_SET_LENGTH_WRONG)

    status = set_bot_name(bot_id, bot_nickname, user_info)

    ## Add by Quentin below
    client_id = user_info.client_id
    client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                      where_clause=BaseModel.and_(
                                          ["=", "client_id", client_id],
                                      ))

    try:
        for client_qun in client_quns:
            data = {
                "task": "update_self_displayname",
                "chatroomname": client_qun.chatroomname,
                "selfdisplayname": bot_nickname
            }
            send_ws_to_android(bot_id, data)
            # data = {"bot_username": bot_id,
            #         "data": {
            #             "task": "update_self_displayname",
            #             "chatroomname": client_qun.chatroomname,
            #             "selfdisplayname": bot_nickname
            #         }}



            # resp = requests.post('http://ardsvr.xuanren360.com/android/send_message', json=data)
            # print "::::::::::::::"
            # print resp
            # if dict(resp.json())['err_code'] == -1:
            #     logger.warning('add_and_send_sensitive_word_log ERROR,because bot dead!')
    except:
        logger.warning('rename bot_nickname error!')

    return make_response(status)


if __name__ == "__main__":
    BaseModel.extract_from_json()

    client_bot = BaseModel.fetch_one("client_bot_r", "*",
                                     where_clause=BaseModel.and_(
                                         ["=", "client_id", 11],
                                         ["=", "bot_username", "wxid_lkruzsl7w2r822"],
                                     ))

    print client_bot.bot_username

    s = BaseModel.fetch_all("client_qun_r", "*",
                            where_clause=BaseModel.and_(
                                ["=", "client_id", 11],
                            ))
    print s.__len__()

    # client_quns = BaseModel.fetch_all("client_qun_r", "*",
    #                                   where_clause=BaseModel.and_(
    #                                       ["=", "client_id", 11],
    #                                   ))
    #
    # print [client_qun.chatroomname for client_qun in client_quns]
    # print client_quns[0].chatroomname
