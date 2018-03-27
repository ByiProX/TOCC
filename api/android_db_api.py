# -*- coding: utf-8 -*-

import logging
from flask import request

from configs.config import SUCCESS, main_api, db
from core.user_core import _bind_bot_success
from core.wechat_core import WechatConn
from models.user_bot_models import BotInfo
from utils.u_email import EmailAlert
from utils.u_model_json_str import verify_json
from utils.u_response import make_response

logger = logging.getLogger('main')


@main_api.route('/android/add_friend', methods=['POST'])
def android_add_friend():
    verify_json()
    user_nickname = request.json.get('user_nickname')
    user_username = request.json.get('user_username')
    bot_username = request.json.get('bot_username')
    bot = db.session.query(BotInfo).filter(BotInfo.username == bot_username).first()

    logger.info(u"发现加bot好友用户. username: %s." % user_username)
    status, user_info = _bind_bot_success(user_nickname, user_username, bot)
    we_conn = WechatConn()
    if status == SUCCESS:
        we_conn.send_txt_to_follower(
            "您好，欢迎使用数字货币友问币答！请将我拉入您要管理的区块链社群，拉入成功后即可为您的群提供实时查询币价，涨幅榜，币种成交榜，交易所榜，最新动态，行业百科等服务。步骤如下：\n拉我入群➡确认拉群成功➡ "
            "机器人在群发自我介绍帮助群友了解规则➡群友按照命令发关键字➡机器人回复➡完毕",
            user_info.open_id)
    # else:
    #     EmailAlert.send_ue_alert(u"有用户尝试绑定机器人，但未绑定成功.疑似网络通信问题. "
    #                              u"user_username: %s." % user_username)

    return make_response(SUCCESS)
