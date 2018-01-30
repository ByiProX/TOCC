# -*- coding: utf-8 -*-
import json

from flask import request

from config import app, SUCCESS
from core.user import UserLogin, add_a_pre_relate_user_bot_info
from utils.u_response import make_response


@app.route('/verify_code', methods=['POST'])
def app_verify_code():
    """
    用于验证
    code: 微信传入的code
    """
    data_json = json.loads(request.data)
    code = data_json.get('code')

    user_login = UserLogin(code)
    status, user_info = user_login.get_user_token()

    if status == SUCCESS:
        return make_response(status, user_info=user_info.to_json())
    else:
        return make_response(status)


@app.route('/set_rebot_nickname', methods=['POST'])
def set_rebot_nickname():
    """
    用于设置rebot名字
    """
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    bot_nickname = request.json.get('bot_nickname')

    status, ubr_info = add_a_pre_relate_user_bot_info(user_info, bot_nickname)

    return make_response(status)


@app.route("/provide_bot_qr_code", methods=["POST"])
def provide_bot_qr_code():
    """
    提供前端一个二维码
    :return:
    """
    # 这里是前端来一个请求，然后返回后端一个图片
    # 可能需要根据bot情况进行负载均衡
    pass


@app.route("/binded_wechat_bot", methods=["POST"])
def binded_wechat_bot():
    """
    当捆绑bot成功时，我应该得到的消息
    :return:
    """
    # 在Contact里面监测新的好友的昵称是否在里面（如果重合报错）
    # 然后我这边确认，这个人是否已经在咱们的系统里面，如果在咱们的系统里面
    # 然后我把这个机器人绑上
    pass

# 进群只能通过Message，
