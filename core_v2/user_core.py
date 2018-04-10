# -*- coding: utf-8 -*-
import base64
import logging
import hashlib

from datetime import datetime, timedelta
from sqlalchemy import func

from configs.config import SUCCESS, TOKEN_EXPIRED_THRESHOLD, ERR_USER_TOKEN_EXPIRED, ERR_USER_LOGIN_FAILED, \
    ERR_USER_TOKEN, ERR_MAXIMUM_BOT, ERR_NO_ALIVE_BOT, INFO_NO_USED_BOT, ERR_WRONG_ITEM, ERR_WRONG_USER_ITEM, \
    ERR_NO_BOT_QR_CODE, ERR_HAVE_SAME_PEOPLE, MSG_TYPE_TXT, MSG_TYPE_SYS, ERR_INVALID_PARAMS, UserInfo, UserSwitch, \
    UserBotR, BotInfo, UserQunR, Chatroom
from core_v2.qun_manage_core import set_default_group
from core_v2.wechat_core import wechat_conn
from models_v2.base_model import BaseModel, CM
from utils.u_time import datetime_to_timestamp_utc_8
from utils.u_transformat import str_to_unicode

logger = logging.getLogger('main')


class UserLogin:
    def __init__(self, code):
        self.code = code
        self.open_id = ""
        self.user_access_token = ""
        self.now_user_info = None
        self.user_info_up_to_date = None

        self._get_open_id_and_user_access_token()

    def _get_open_id_and_user_access_token(self):
        """
        根据前端微信返回的code，去wechat的api处调用open_id
        """
        res_json = wechat_conn.get_open_id_by_code(code=self.code)
        self.open_id = res_json.get('openid')
        self.user_access_token = res_json.get('access_token')

    def get_user_token(self):
        """
        从微信处得到open_id，然后通过open得到token
        """
        # 如果没有读取到open_id
        if self.open_id is None:
            self.now_user_info = BaseModel.fetch_one(UserInfo, '*', where_clause = BaseModel.where("=", "code", self.code))
            # 如果这个code和上次code一样
            if self.now_user_info:
                if datetime_to_timestamp_utc_8(datetime.now()) < self.now_user_info.token_expired_time:
                    return SUCCESS, self.now_user_info
                else:
                    logger.error(
                        ERR_USER_TOKEN_EXPIRED +
                        u"code微信不认可，库中有code，但token已经过期. code: %s" % self.code)
                    return ERR_USER_TOKEN_EXPIRED, None
            # 如果这个code在库中查不到
            else:
                logger.error(ERR_USER_LOGIN_FAILED +
                             u"code微信不认可，库中无该code. code: %s" % self.code)
                return ERR_USER_LOGIN_FAILED, None
        else:
            self._get_user_info_from_wechat()
            # 抓到了信息，那么所有信息都更新
            if self.user_info_up_to_date:
                self.now_user_info = BaseModel.fetch_one(UserInfo, '*', where_clause = BaseModel.where("=", "open_id", self.open_id))
                # 意味着之前有，现在也有
                if self.now_user_info:
                    self.now_user_info.code = self.code
                    self.now_user_info.last_login_time = datetime_to_timestamp_utc_8(datetime.now())

                    if datetime_to_timestamp_utc_8(datetime.now()) < self.now_user_info.token_expired_time:
                        logger.info(u"老用户登录，token未过期. user_id: %s" % self.now_user_info.client_id)
                        pass
                    else:
                        self.now_user_info.token = self._generate_user_token()
                        self.now_user_info.token_expired_time = datetime_to_timestamp_utc_8(datetime.now() + timedelta(days=TOKEN_EXPIRED_THRESHOLD))
                        logger.info(u"老用户登录，token更新. user_id: %s" % self.now_user_info.client_id)

                    self.now_user_info.save()
                    return SUCCESS, self.now_user_info
                else:
                    self.user_info_up_to_date.code = self.code
                    self.user_info_up_to_date.create_time = datetime_to_timestamp_utc_8(datetime.now())
                    self.user_info_up_to_date.last_login_time = datetime_to_timestamp_utc_8(datetime.now())

                    self.user_info_up_to_date.token = self._generate_user_token()
                    self.user_info_up_to_date.token_expired_time = datetime_to_timestamp_utc_8(datetime.now() + timedelta(days=TOKEN_EXPIRED_THRESHOLD))

                    # switch
                    user_switch = CM(UserSwitch)
                    self.user_info_up_to_date.func_send_qun_messages = False
                    self.user_info_up_to_date.func_qun_sign = False
                    self.user_info_up_to_date.func_auto_reply = False
                    self.user_info_up_to_date.func_welcome_message = False
                    self.user_info_up_to_date.func_real_time_quotes = False
                    self.user_info_up_to_date.func_synchronous_announcement = False
                    self.user_info_up_to_date.func_coin_wallet = False

                    user_switch.save()
                    self.user_info_up_to_date.save()
                    logger.info(u"新用户登录. user_id: %s" % self.user_info_up_to_date.client_id)
                    return SUCCESS, self.user_info_up_to_date

            # 因为各种原因没有拿到用户信息
            else:
                self.now_user_info = BaseModel.fetch_one(UserInfo, '*', where_clause = BaseModel.where("=", "open_id", self.open_id))
                if self.now_user_info:
                    if datetime_to_timestamp_utc_8(datetime.now()) < self.now_user_info.token_expired_time:
                        logger.warning(u"老用户登录，微信不认可open_id. user_id: %s" % self.now_user_info.client_id)
                        return SUCCESS, self.now_user_info
                    else:
                        logger.warning(u"老用户登录，token过期. user_id: %s" % self.now_user_info.client_id)
                        return ERR_USER_TOKEN_EXPIRED, None
                else:
                    logger.error(u"微信不认可open_id，未知用户. code: %s" % self.code)
                    return ERR_USER_LOGIN_FAILED, None

    @staticmethod
    def verify_token(token):
        if not token:
            return ERR_INVALID_PARAMS, None
        user_info = BaseModel.fetch_one(UserInfo, '*', where_clause = BaseModel.where("=", "token", token))
        if user_info:
            if datetime_to_timestamp_utc_8(datetime.now()) < user_info.token_expired_time:
                logger.debug(u"用户token有效")
                return SUCCESS, user_info
            else:
                logger.error(
                    u"用户token过期. user_id: %s. 过期时间: %s" % (user_info.client_id, str(user_info.token_expired_time)))
                return ERR_USER_TOKEN_EXPIRED, None
        else:
            logger.error(u"无效用户token. token: %s" % token)
            return ERR_USER_TOKEN, None

    def _get_user_info_from_wechat(self):
        res_json = wechat_conn.get_user_info(open_id=self.open_id, user_access_token=self.user_access_token)

        if res_json.get('openid'):
            self.user_info_up_to_date = CM(UserInfo)
            self.user_info_up_to_date.open_id = res_json.get('openid')
            self.user_info_up_to_date.union_id = res_json.get('unionid')
            self.user_info_up_to_date.nick_name = res_json.get('nickname')
            self.user_info_up_to_date.sex = res_json.get('sex')
            self.user_info_up_to_date.province = res_json.get('province')
            self.user_info_up_to_date.city = res_json.get('city')
            self.user_info_up_to_date.country = res_json.get('country')
            self.user_info_up_to_date.avatar_url = res_json.get('avatar_url')

            self.user_info_up_to_date.username = ""

        # 获取wechat端信息失败
        else:
            pass

    def _generate_user_token(self, open_id=None, datetime_now=None):
        if open_id and datetime_now:
            self.open_id = open_id
            datetime_now = datetime_to_timestamp_utc_8(datetime_now)
        else:
            datetime_now = datetime_to_timestamp_utc_8(datetime.now())

        if self.open_id is None:
            raise ValueError("没有正确的open_id")

        pre_str = self.open_id.upper() + str(datetime_now) + "stvrhu"
        m2 = hashlib.md5()
        m2.update(pre_str)
        token = m2.hexdigest()
        return token


def set_bot_name(bot_id, bot_nickname, user_info):
    bot_info = BaseModel.fetch_by_id(BotInfo, bot_id)
    ubr_info = BaseModel.fetch_one(UserBotR, '*', where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                       "bot_username": bot_info.username}))

    if not ubr_info:
        logger.error(u"未找到已开启的user与bot关系. user_id: %s. bot_id: %s." % (user_info.user_id, bot_id))
        return ERR_WRONG_USER_ITEM

    ubr_info.chatbot_default_nickname = bot_nickname
    ubr_info.save()
    logger.info(u"已更新全局bot名称. bot_id: %s. bot_nickname: %s" % (bot_id, bot_nickname))
    return SUCCESS


def add_a_pre_relate_user_bot_info(user_info, chatbot_default_nickname):
    ubr_info_list = CM(UserBotR).fetch_all('*', where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    if len(ubr_info_list) > 1:
        raise ValueError(u"已经有多于一个机器人，不可以再预设置机器人")
    elif len(ubr_info_list) == 1:
        if ubr_info_list[0].is_setted:
            logger.error(u"已经有设置完成的bot. user_id: %s." % user_info.user_id)
            return ERR_MAXIMUM_BOT, None
        else:
            ubr_info = ubr_info_list[0]
    else:
        ubr_info = CM(UserBotR)

    ubr_info.client_id = user_info.client_id

    bot_info = _get_a_balanced_bot()
    if not bot_info:
        logger.error(u"未取得可用bot. user_id: %s" % user_info.client_id)
        return ERR_NO_ALIVE_BOT, None

    ubr_info.bot_username = bot_info.username

    ubr_info.chatbot_default_nickname = chatbot_default_nickname
    ubr_info.is_work = False
    ubr_info.create_time = datetime_to_timestamp_utc_8(datetime.now())

    ubr_info.save()
    logger.info(u"初始化user与bot关系成功. user_id: %s. bot_username: %s." % (user_info.client_id, bot_info.bot_username))
    return SUCCESS, ubr_info


def cal_user_basic_page_info(user_info):
    ubr_info = BaseModel.fetch_one(UserBotR, '*', where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))

    if ubr_info:
        uqr_info = BaseModel.fetch_one(UserQunR, '*', where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
        group_list = uqr_info.group_list
        chatroomname_set = set()
        for group in group_list:
            for chatroomname in group.values()[0]:
                chatroomname_set.add(chatroomname)
        qun_count = len(chatroomname_set)
        if not chatroomname_set:
            # 目前没有控制的群，不需要下一步统计
            logger.debug(u"无绑定群. user_id: %s." % user_info.user_id)
            member_count = 0
            pass
        else:
            chatroomname_list = list(chatroomname_set)
            chatroom_list = CM(Chatroom).fetch_all(select_colums = ["chatroomname", "member_count"], where_clause = BaseModel.where("in", "chatroomname", chatroomname_list))
            member_count = 0
            for chatroom in chatroom_list:
                member_count += chatroom.member_count

        res = dict()
        res.setdefault("bot_info", {})
        # TODO: bot_id encode
        # res['bot_info'].setdefault('bot_id', ubr_info.bot_id)
        # res['bot_info'].setdefault('chatbot_nickname', ubr_info.chatbot_default_nickname)
        # bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == ubr_info.bot_id).first()
        # if not bot_info:
        #     logger.error(u"bot信息出错. bot_id: %s" % ubr_info.bot_id)
        #     return ERR_WRONG_ITEM, None
        # if bot_info.is_alive is True:
        #     bot_status = 0
        # else:
        #     bot_status = -1
        # res['bot_info'].setdefault('bot_status', bot_status)
        # a_bot = db.session.query(ABot).filter(ABot.username == bot_info.username).first()
        # if not a_bot:
        #     logger.error(u"bot信息出错. bot_id: %s" % ubr_info.bot_id)
        #     return ERR_WRONG_ITEM, None
        # res['bot_info'].setdefault('bot_avatar', a_bot.avatar_url2)
        #
        # username = a_bot.username
        # img_str = _get_qr_code_base64_str(username)
        # res['bot_info'].setdefault('bot_qr_code', img_str)
        #
        # res.setdefault("total_info", {})
        # res['total_info'].setdefault('qun_count', qun_count)
        # res['total_info'].setdefault('cover_member_count', member_count)
        #
        # res.setdefault("user_func", {})
        # res['user_func'].setdefault('func_send_messages', user_info.func_send_qun_messages)
        # res['user_func'].setdefault('func_sign', user_info.func_qun_sign)
        # res['user_func'].setdefault('func_reply', user_info.func_auto_reply)
        # res['user_func'].setdefault('func_welcome', user_info.func_welcome_message)
        # res['user_func'].setdefault('func_real_time_quotes', user_info.func_real_time_quotes)
        # res['user_func'].setdefault('func_synchronous_announcement', user_info.func_synchronous_announcement)
        # res['user_func'].setdefault('func_coin_wallet', user_info.func_coin_wallet)
        # logger.info(u"返回有机器人时群组列表. user_id: %s." % user_info.user_id)
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
        res['user_func'].setdefault('func_real_time_quotes', False)
        res['user_func'].setdefault('func_synchronous_announcement', False)
        res['user_func'].setdefault('func_coin_wallet', False)
        logger.info(u"返回无机器人时群组列表. user_id: %s." % user_info.user_id)
        return INFO_NO_USED_BOT, res


def get_bot_qr_code(user_info):
    ubr_info = BaseModel.fetch_one(UserBotR, '*', where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))

    if not ubr_info:
        logger.error(u"无预建立的群关系. user_id: %s." % user_info.user_id)
        return ERR_WRONG_USER_ITEM, None

    bot_info = BaseModel.fetch_one(BotInfo, "*", where_clause = BaseModel.where_dict({"username": ubr_info.bot_username}))

    if not bot_info:
        logger.error(u"bot信息出错. bot_id: %s" % ubr_info.bot_id)
        return ERR_WRONG_ITEM, None

    username = bot_info.username
    img_str = _get_qr_code_base64_str(username)

    if not img_str:
        logger.error(u"static中无bot的QR信息. bot_id: %s. bot_username: %s." % (ubr_info.bot_id, username))
        return ERR_NO_BOT_QR_CODE, None

    logger.info(u"返回QR码. bot_id: %s." % ubr_info.bot_id)
    return SUCCESS, img_str


def _bind_bot_success(user_nickname, user_username, bot_info):
    """
    确认将一个bot绑入一个user之中
    :return:
    """

    # 因为AFriend等库更新未必在Message之前（在网速较慢的情况下可能出现）
    # 所以此处先sleep一段时间，等待AFriend更新后再读取
    # time.sleep(5)

    # 验证是否是好友
    # a_friend = AFriend.get_a_friend(from_username = bot_info.username,
    #                                 to_username = user_username)
    # if not a_friend:
    #     logger.error(u"好友信息出错. bot_username: %s. user_username: %s" %
    #                  (bot_info.username, user_username))
    #     return ERR_WRONG_ITEM, None
    #
    # if a_friend.type % 2 != 1:
    #     logger.error(u"用户与bot不是好友. bot_username: %s. user_username: %s" %
    #                  (bot_info.username, user_username))
    #     logger.info(u'但是放宽限制，暂时给予通过')
    #     # return ERR_WRONG_ITEM, None

    user_info_list = CM(UserInfo).fetch_all('*', where_clause = BaseModel.where_dict({"nickname": user_nickname, "username": u""}))
    if len(user_info_list) > 1:
        logger.error(u"根据username无法确定其身份. bot_username: %s. user_username: %s" %
                     (bot_info.username, user_username))
        return ERR_HAVE_SAME_PEOPLE, None
    elif len(user_info_list) == 0:
        logger.error(u"配对user信息出错，可能是已经绑定成功. bot_username: %s. user_username: %s" %
                     (bot_info.username, user_username))
        return ERR_WRONG_ITEM, None

    # user_info_list_2 = db.session.query(UserInfo).filter(UserInfo.username == user_username).all()
    # if user_info_list_2:
    #     logger.error(u"已绑定username与user关系. bot_username: %s. user_username: %s" %
    #                  (bot_info.username, user_username))
    #     return ERR_HAVE_SAME_PEOPLE, None

    user_info = user_info_list[0]
    user_info.username = user_username
    user_info.save()

    user_switch = CM(UserSwitch)
    user_switch.client_id = user_info.client_id
    user_switch.func_send_qun_messages = True
    user_switch.func_auto_reply = False
    user_switch.func_real_time_quotes = True
    user_switch.func_synchronous_announcement = True
    user_switch.func_coin_wallet = False
    user_switch.save()

    logger.debug(u"完成绑定user与username关系. user_id: %s. username: %s." % (user_info.user_id, user_username))
    ubr_info = BaseModel.fetch_one(UserBotR, '*', where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                "bot_username": bot_info.username}))
    if not ubr_info:
        logger.debug(u"没有完成bot与user的预绑定过程. user_id: %s." % user_info.user_id)
        ubr_info = CM(UserBotR)
        ubr_info.client_id = user_info.client_id
        ubr_info.bot_username = bot_info.username
        ubr_info.is_work = True
        ubr_info.save()

    ubr_info.is_work = True
    ubr_info.save()

    set_default_group(user_info.client_id)
    logger.info(u"已绑定bot与user关系. user_id: %s. bot_id: %s." % (user_info.user_id, bot_info.bot_id))
    return SUCCESS, user_info


def _get_a_balanced_bot():
    """
    得到一个平衡过数量的bot
    :return:
    """
    # TODO: _get_a_balanced_bot

    # bot_info_list = db.session.query(BotInfo).all()
    # bot_used_dict = dict()
    # for bot_info in bot_info_list:
    #     bot_used_dict.setdefault(bot_info.bot_id, 0)
    #     ugc = db.session.query(func.count(UserBotRelateInfo.user_id)).filter(
    #         UserBotRelateInfo.bot_id == bot_info.bot_id, UserBotRelateInfo.is_being_used == 1).first()
    #     if ugc:
    #         bot_used_dict[bot_info.bot_id] = int(ugc[0])
    #
    # ugls = sorted(bot_used_dict.items(), key=lambda d: d[1])
    # if ugls:
    #     for eug in ugls:
    #         bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == eug[0], BotInfo.is_alive == 1).first()
    #         if bot_info:
    #             return bot_info
    #
    # return None
    return BaseModel.fetch_one(BotInfo, '*')


def _get_qr_code_base64_str(username):
    try:
        f = open("static/bot_qr_code/" + str(username) + ".jpg", 'r')
    except IOError:
        logger.warning(u"无该username(%s)的qr_code." % str(username))
        return None
    img_str = base64.b64encode(f.read())
    f.close()
    return img_str
