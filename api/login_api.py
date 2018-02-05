# -*- coding: utf-8 -*-
import json

from flask import request

from configs.config import SUCCESS, main_api, INFO_NO_USED_BOT, ERR_SET_LENGTH_WRONG, ERR_INVALID_PARAMS, ERR_PARAM_SET
from core.user_core import UserLogin, add_a_pre_relate_user_bot_info, cal_user_basic_page_info, get_bot_qr_code, \
    set_bot_name
from utils.u_response import make_response


@main_api.route('/verify_code', methods=['POST'])
def app_verify_code():
    """
    用于验证
    code: 微信传入的code
    {"code":"111"}
    """
    if not request.data:
        return make_response(ERR_PARAM_SET)
    data_json = json.loads(request.data)
    code = data_json.get('code')
    if not code:
        return make_response(ERR_INVALID_PARAMS)

    user_login = UserLogin(code)
    status, user_info = user_login.get_user_token()
    # TODO 这里有bug
    if status == SUCCESS:
        return make_response(status, user_info=user_info.to_dict())
    else:
        return make_response(status)


@main_api.route('/get_user_basic_info', methods=['POST'])
def app_get_user_basic_info():
    """
    读取用户管理界面的所有的信息
    {"token":"test_token_123"}
    """
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


@main_api.route('/initial_robot_nickname', methods=['POST'])
def app_initial_robot_nickname():
    """
    用于设置robot名字,并返回二维码
    {"token":"test_token_123","bot_nickname":"测试呀测试"}
    """
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


@main_api.route('/set_robot_nickname', methods=['POST'])
def app_set_robot_nickname():
    """
    用于设置rebot名字
    """
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

    status, ubr_info = set_bot_name(bot_id, bot_nickname, user_info)

    return make_response(status)


@main_api.route("/get_bot_qr_code", methods=["POST"])
def app_get_bot_qr_code():
    """
    提供前端一个二维码
    :return:
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    status, res = get_bot_qr_code(user_info)

    if status == SUCCESS:
        return make_response(status, qr_code=res)
    else:
        return make_response(status)


@main_api.route("/binded_wechat_bot", methods=["POST"])
def app_binded_wechat_bot():
    """
    当捆绑bot成功时，我应该得到的消息
    :return:
    """
    pass

# 进群只能通过Message，
