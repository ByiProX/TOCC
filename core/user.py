# -*- coding: utf-8 -*-
import base64
import logging
import hashlib

from datetime import datetime, timedelta
from sqlalchemy import func

from config import db, SUCCESS, TOKEN_EXPIRED_THRESHOLD, ERR_USER_TOKEN_EXPIRED, ERR_USER_LOGIN_FAILED, \
    ERR_USER_TOKEN, ERR_MAXIMUM_BOT, ERR_NO_ALIVE_BOT, INFO_NO_USED_BOT, ERR_WRONG_ITEM, ERR_WRONG_USER_ITEM, \
    ERR_NO_BOT_QR_CODE
from core.wechat import WechatConn
from models.android_db import AContact, ABot
from models.qun_friend import UserQunRelateInfo
from models.user_bot import UserInfo, UserBotRelateInfo, BotInfo

logger = logging.getLogger('main')


class UserLogin:
    def __init__(self, code):
        self.code = code
        self.open_id = ""
        self.user_access_token = ""
        self.now_user_info = None
        self.user_info_up_to_date = None
        self.wechat_conn = WechatConn()

        self._get_open_id_and_user_access_token()

    def _get_open_id_and_user_access_token(self):
        """
        根据前端微信返回的code，去wechat的api处调用open_id
        """
        res_json = self.wechat_conn.get_open_id_by_code(code=self.code)
        self.open_id = res_json.get('openid')
        self.user_access_token = res_json.get('access_token')

    def get_user_token(self):
        """
        从微信处得到open_id，然后通过open得到token
        """
        # 如果没有读取到open_id
        if self.open_id is None:
            self.now_user_info = db.session.query(UserInfo).filter(UserInfo.code == self.code).first()
            # 如果这个code和上次code一样
            if self.now_user_info:
                if datetime.now() < self.now_user_info.token_expired_time:
                    return SUCCESS, self.now_user_info
                else:
                    return ERR_USER_TOKEN_EXPIRED, None
            # 如果这个code在库中查不到
            else:
                return ERR_USER_LOGIN_FAILED, None
        else:
            self._get_user_info_from_wechat()
            # 抓到了信息，那么所有信息都更新
            if self.user_info_up_to_date:
                self.now_user_info = db.session.query(UserInfo).filter(UserInfo.open_id == self.open_id).first()
                # 意味着之前有，现在也有
                if self.now_user_info:
                    self.user_info_up_to_date.code = self.code
                    self.user_info_up_to_date.last_login_time = datetime.now()

                    if datetime.now() < self.now_user_info.token_expired_time:
                        pass
                    else:
                        self.user_info_up_to_date.token = self._generate_user_token()
                        self.user_info_up_to_date.token_expired_time = datetime.now() + timedelta(
                            days=TOKEN_EXPIRED_THRESHOLD)

                    db.session.merge(self.user_info_up_to_date)
                    db.session.commit()
                    return SUCCESS, self.user_info_up_to_date
                else:
                    self.user_info_up_to_date.code = self.code
                    self.user_info_up_to_date.create_time = datetime.now()
                    self.user_info_up_to_date.last_login_time = datetime.now()

                    self.user_info_up_to_date.token = self._generate_user_token()
                    self.user_info_up_to_date.token_expired_time = datetime.now() + timedelta(
                        days=TOKEN_EXPIRED_THRESHOLD)

                    self.user_info_up_to_date.func_send_qun_messages = False
                    self.user_info_up_to_date.func_qun_sign = False
                    self.user_info_up_to_date.func_auto_reply = False
                    self.user_info_up_to_date.func_welcome_message = False

                    db.session.add(self.user_info_up_to_date)
                    db.session.commit()
                    return SUCCESS, self.user_info_up_to_date

            # 因为各种原因没有拿到用户信息
            else:
                self.now_user_info = db.session.query(UserInfo).filter(UserInfo.open_id == self.open_id).first()
                if self.now_user_info:
                    if datetime.now() < self.now_user_info.token_expired_time:
                        return SUCCESS, self.now_user_info
                    else:
                        return ERR_USER_TOKEN_EXPIRED, None
                else:
                    return ERR_USER_LOGIN_FAILED, None

    @staticmethod
    def verify_token(token):
        user_info = db.session.query(UserInfo).filter(UserInfo.token == token).first()
        if user_info:

            if datetime.now() < user_info.token_expired_time:
                return SUCCESS, user_info
            else:
                return ERR_USER_TOKEN_EXPIRED, None
        else:
            return ERR_USER_TOKEN, None

    def _get_user_info_from_wechat(self):
        res_json = self.wechat_conn.get_user_info(open_id=self.open_id, user_access_token=self.user_access_token)

        if res_json.get('openid'):
            self.user_info_up_to_date = UserInfo()
            self.user_info_up_to_date.open_id = res_json.get('openid')
            self.user_info_up_to_date.union_id = res_json.get('unionid')
            self.user_info_up_to_date.nick_name = res_json.get('nick_name')
            self.user_info_up_to_date.sex = res_json.get('sex')
            self.user_info_up_to_date.province = res_json.get('province')
            self.user_info_up_to_date.city = res_json.get('city')
            self.user_info_up_to_date.country = res_json.get('country')
            self.user_info_up_to_date.avatar_url = res_json.get('avatar_url')

        # 获取wechat端信息失败
        else:
            pass

    def _generate_user_token(self, open_id=None, datetime_now=None):
        if open_id and datetime_now:
            self.open_id = open_id
            datetime_now = datetime_now
        else:
            datetime_now = datetime.now()

        if self.open_id is None:
            raise ValueError("没有正确的open_id")

        pre_str = self.open_id.upper() + str(datetime_now) + "stvrhu"
        m2 = hashlib.md5()
        m2.update(pre_str)
        token = m2.hexdigest()
        return token


def set_bot_name(bot_id, bot_nickname, user_info):
    ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.bot_id == bot_id,
                                                          UserBotRelateInfo.user_id == user_info.user_id,
                                                          UserBotRelateInfo.is_setted == 1).first()

    if not ubr_info:
        return ERR_WRONG_USER_ITEM

    ubr_info.chatbot_default_nickname = bot_nickname
    db.session.commit()
    return SUCCESS


def add_a_pre_relate_user_bot_info(user_info, chatbot_default_nickname):
    ubr_info_list = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_info.user_id).all()
    if len(ubr_info_list) > 1:
        raise ValueError("已经有多于一个机器人，不可以再预设置机器人")
    elif len(ubr_info_list) == 1:
        if ubr_info_list[0].is_setted:
            return ERR_MAXIMUM_BOT, None
        else:
            ubr_info = ubr_info_list[0]
    else:
        ubr_info = UserBotRelateInfo()

    ubr_info.user_id = user_info.user_id

    bot_info = _get_a_balanced_bot()
    if not bot_info:
        return ERR_NO_ALIVE_BOT, None

    ubr_info.bot_id = bot_info.bot_id

    ubr_info.chatbot_default_nickname = chatbot_default_nickname
    ubr_info.preset_time = datetime.now()
    ubr_info.set_time = 0
    ubr_info.is_setted = False
    ubr_info.is_being_used = False

    db.session.add(ubr_info)
    db.session.commit()

    return SUCCESS, ubr_info


def cal_user_basic_page_info(user_info):
    ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_info.user_id,
                                                          UserBotRelateInfo.is_setted == 0).first()

    if ubr_info:
        uqr_info_list = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == user_info.user_id,
                                                                   UserQunRelateInfo.is_deleted == 0).all()
        qun_count = len(uqr_info_list)
        if not uqr_info_list:
            # 目前没有控制的群，不需要下一步统计
            member_count = 0
            pass
        else:
            chatroomname_list = []
            for uqr_info in uqr_info_list:
                chatroomname_list.append(uqr_info.chatroomname)

            member_count = db.session.query(func.sum(AContact.member_count)).filter(
                AContact.username.in_(chatroomname_list)).first()

        res = dict()
        res.setdefault("bot_info", {})
        res['bot_info'].setdefault('bot_id', ubr_info.bot_id)
        res['bot_info'].setdefault('chatbot_nickname', ubr_info.chatbot_default_nickname)
        bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == ubr_info.bot_id).first()
        if not bot_info:
            return ERR_WRONG_ITEM, None
        res['bot_info'].setdefault('bot_status', bot_info.is_alive)
        a_bot = db.session.query(ABot).filter(ABot.username == bot_info.username).first()
        if not a_bot:
            return ERR_WRONG_ITEM, None
        res['bot_info'].setdefault('bot_avatar', a_bot.avatar_url2)

        username = a_bot.username
        img_str = _get_qr_code_base64_str(username)
        res['bot_info'].setdefault('bot_qr_code', img_str)

        res.setdefault("total_info", {})
        res['total_info'].setdefault('qun_count', qun_count)
        res['total_info'].setdefault('cover_member_count', member_count)

        res.setdefault("user_func", {})
        res['user_func'].setdefault('func_send_messages', user_info.func_send_qun_messages)
        res['user_func'].setdefault('func_sign', user_info.func_qun_sign)
        res['user_func'].setdefault('func_reply', user_info.func_auto_reply)
        res['user_func'].setdefault('func_welcome', user_info.func_welcome_message)
        return SUCCESS, res

    # 用户目前没有机器人
    else:
        res = dict()
        res.setdefault("bot_info", None)
        res.setdefault("total_info", {})
        res['total_info'].setdefault('qun_count', 0)
        res['total_info'].setdefault('cover_member_count', 0)
        res.setdefault("user_func", {})
        res['user_func'].setdefault('func_send_messages', False)
        res['user_func'].setdefault('func_sign', False)
        res['user_func'].setdefault('func_reply', False)
        res['user_func'].setdefault('func_welcome', False)
        return INFO_NO_USED_BOT, res


def get_bot_qr_code(user_info):
    ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_info.user_id,
                                                          UserBotRelateInfo.is_setted == 0).first()

    if not ubr_info:
        return ERR_WRONG_USER_ITEM, None

    bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == ubr_info.bot_id).first()

    if not bot_info:
        return ERR_WRONG_ITEM, None

    username = bot_info.username
    img_str = _get_qr_code_base64_str(username)

    if not img_str:
        return ERR_NO_BOT_QR_CODE, None

    return SUCCESS, img_str


def _get_a_balanced_bot():
    """
    得到一个平衡过数量的bot
    :return:
    """

    bot_info_list = db.session.query(BotInfo).all()
    bot_used_dict = dict()
    for bot_info in bot_info_list:
        bot_used_dict.setdefault(bot_info.bot_id, 0)
        ugc = db.session.query(func.count(UserBotRelateInfo.user_id)).filter(
            UserBotRelateInfo.bot_id == bot_info.bot_id, UserBotRelateInfo.is_being_used == 1).first()
        if ugc:
            bot_used_dict[bot_info.bot_id] = int(ugc[0])

    ugls = sorted(bot_used_dict.items(), key=lambda d: d[1])
    if ugls:
        for eug in ugls:
            bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == eug[0], BotInfo.is_alive == 1).first()
            if bot_info:
                return bot_info

    return None


def _get_qr_code_base64_str(username):
    try:
        f = open("static/bot_qr_code/" + str(username) + ".jpg", 'r')
    except IOError:
        logger.warning("无该username(%s)的qr_code." % str(username))
        return None
    img_str = base64.b64encode(f.read())
    f.close()
    return img_str
