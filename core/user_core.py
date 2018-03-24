# -*- coding: utf-8 -*-
import base64
import logging
import hashlib

from datetime import datetime, timedelta
from sqlalchemy import func

from configs.config import db, SUCCESS, TOKEN_EXPIRED_THRESHOLD, ERR_USER_TOKEN_EXPIRED, ERR_USER_LOGIN_FAILED, \
    ERR_USER_TOKEN, ERR_MAXIMUM_BOT, ERR_NO_ALIVE_BOT, INFO_NO_USED_BOT, ERR_WRONG_ITEM, ERR_WRONG_USER_ITEM, \
    ERR_NO_BOT_QR_CODE, ERR_HAVE_SAME_PEOPLE, MSG_TYPE_TXT, MSG_TYPE_SYS, ERR_INVALID_PARAMS
from core.qun_manage_core import set_default_group
from core.wechat_core import WechatConn
from models.android_db_models import AContact, ABot, AFriend
from models.qun_friend_models import UserQunRelateInfo
from models.user_bot_models import UserInfo, UserBotRelateInfo, BotInfo
from utils.u_email import EmailAlert
from utils.u_transformat import str_to_unicode

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
                self.now_user_info = db.session.query(UserInfo).filter(UserInfo.open_id == self.open_id).first()
                # 意味着之前有，现在也有
                if self.now_user_info:
                    self.now_user_info.code = self.code
                    self.now_user_info.last_login_time = datetime.now()

                    if datetime.now() < self.now_user_info.token_expired_time:
                        logger.info(u"老用户登录，token未过期. user_id: %s" % self.now_user_info.user_id)
                        pass
                    else:
                        self.now_user_info.token = self._generate_user_token()
                        self.now_user_info.token_expired_time = datetime.now() + timedelta(
                            days=TOKEN_EXPIRED_THRESHOLD)
                        logger.info(u"老用户登录，token更新. user_id: %s" % self.now_user_info.user_id)

                    db.session.merge(self.now_user_info)
                    db.session.commit()
                    return SUCCESS, self.now_user_info
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
                    self.user_info_up_to_date.func_real_time_quotes = False
                    self.user_info_up_to_date.func_synchronous_announcement = False
                    self.user_info_up_to_date.func_coin_wallet = False

                    db.session.add(self.user_info_up_to_date)
                    db.session.commit()
                    logger.info(u"新用户登录. user_id: %s" % self.user_info_up_to_date.user_id)
                    return SUCCESS, self.user_info_up_to_date

            # 因为各种原因没有拿到用户信息
            else:
                self.now_user_info = db.session.query(UserInfo).filter(UserInfo.open_id == self.open_id).first()
                if self.now_user_info:
                    if datetime.now() < self.now_user_info.token_expired_time:
                        logger.warning(u"老用户登录，微信不认可open_id. user_id: %s" % self.now_user_info.user_id)
                        return SUCCESS, self.now_user_info
                    else:
                        logger.warning(u"老用户登录，token过期. user_id: %s" % self.now_user_info.user_id)
                        return ERR_USER_TOKEN_EXPIRED, None
                else:
                    logger.error(u"微信不认可open_id，未知用户. code: %s" % self.code)
                    return ERR_USER_LOGIN_FAILED, None

    @staticmethod
    def verify_token(token):
        if not token:
            return ERR_INVALID_PARAMS, None
        user_info = db.session.query(UserInfo).filter(UserInfo.token == token).first()
        if user_info:
            if datetime.now() < user_info.token_expired_time:
                logger.debug(u"用户token有效")
                return SUCCESS, user_info
            else:
                logger.error(
                    u"用户token过期. user_id: %s. 过期时间: %s" % (user_info.user_id, str(user_info.token_expired_time)))
                return ERR_USER_TOKEN_EXPIRED, None
        else:
            logger.error(u"无效用户token. token: %s" % token)
            return ERR_USER_TOKEN, None

    def _get_user_info_from_wechat(self):
        res_json = self.wechat_conn.get_user_info(open_id=self.open_id, user_access_token=self.user_access_token)

        if res_json.get('openid'):
            self.user_info_up_to_date = UserInfo()
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
        logger.error(u"未找到已开启的user与bot关系. user_id: %s. bot_id: %s." % (user_info.user_id, bot_id))
        return ERR_WRONG_USER_ITEM

    ubr_info.chatbot_default_nickname = bot_nickname
    db.session.commit()
    logger.info(u"已更新全局bot名称. bot_id: %s. bot_nickname: %s" % (bot_id, bot_nickname))
    return SUCCESS


def add_a_pre_relate_user_bot_info(user_info, chatbot_default_nickname):
    ubr_info_list = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_info.user_id).all()
    if len(ubr_info_list) > 1:
        raise ValueError(u"已经有多于一个机器人，不可以再预设置机器人")
    elif len(ubr_info_list) == 1:
        if ubr_info_list[0].is_setted:
            logger.error(u"已经有设置完成的bot. user_id: %s." % user_info.user_id)
            return ERR_MAXIMUM_BOT, None
        else:
            ubr_info = ubr_info_list[0]
    else:
        ubr_info = UserBotRelateInfo()

    ubr_info.user_id = user_info.user_id

    bot_info = _get_a_balanced_bot()
    if not bot_info:
        logger.error(u"未取得可用bot. user_id: %s" % user_info.user_id)
        return ERR_NO_ALIVE_BOT, None

    ubr_info.bot_id = bot_info.bot_id

    ubr_info.chatbot_default_nickname = chatbot_default_nickname
    ubr_info.preset_time = datetime.now()
    ubr_info.set_time = 0
    ubr_info.is_setted = False
    ubr_info.is_being_used = False

    db.session.add(ubr_info)
    db.session.commit()
    logger.info(u"初始化user与bot关系成功. user_id: %s. bot_id: %s." % (user_info.user_id, bot_info.bot_id))
    return SUCCESS, ubr_info


def cal_user_basic_page_info(user_info):
    ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_info.user_id,
                                                          UserBotRelateInfo.is_setted == 1,
                                                          UserBotRelateInfo.is_being_used == 1).first()

    if ubr_info:
        uqr_info_list = db.session.query(UserQunRelateInfo).filter(UserQunRelateInfo.user_id == user_info.user_id,
                                                                   UserQunRelateInfo.is_deleted == 0).all()
        qun_count = len(uqr_info_list)
        if not uqr_info_list:
            # 目前没有控制的群，不需要下一步统计
            logger.debug(u"无绑定群. user_id: %s." % user_info.user_id)
            member_count = 0
            pass
        else:
            chatroomname_list = []
            for uqr_info in uqr_info_list:
                chatroomname_list.append(uqr_info.chatroomname)

            member_count = db.session.query(func.sum(AContact.member_count)).filter(
                AContact.username.in_(chatroomname_list)).first()
            if member_count is None:
                member_count = 0
            else:

                member_count = int(member_count[0])

        res = dict()
        res.setdefault("bot_info", {})
        res['bot_info'].setdefault('bot_id', ubr_info.bot_id)
        res['bot_info'].setdefault('chatbot_nickname', ubr_info.chatbot_default_nickname)
        bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == ubr_info.bot_id).first()
        if not bot_info:
            logger.error(u"bot信息出错. bot_id: %s" % ubr_info.bot_id)
            return ERR_WRONG_ITEM, None
        if bot_info.is_alive is True:
            bot_status = 0
        else:
            bot_status = -1
        res['bot_info'].setdefault('bot_status', bot_status)
        a_bot = db.session.query(ABot).filter(ABot.username == bot_info.username).first()
        if not a_bot:
            logger.error(u"bot信息出错. bot_id: %s" % ubr_info.bot_id)
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
        res['user_func'].setdefault('func_real_time_quotes', user_info.func_real_time_quotes)
        res['user_func'].setdefault('func_synchronous_announcement', user_info.func_synchronous_announcement)
        res['user_func'].setdefault('func_coin_wallet', user_info.func_coin_wallet)
        logger.info(u"返回有机器人时群组列表. user_id: %s." % user_info.user_id)
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
    ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_info.user_id).first()

    if not ubr_info:
        logger.error(u"无预建立的群关系. user_id: %s." % user_info.user_id)
        return ERR_WRONG_USER_ITEM, None

    bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == ubr_info.bot_id).first()

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


def check_whether_message_is_add_friend(message_analysis):
    """
    根据一条Message，返回是否为加bot为好友
    :return:
    """
    is_add_friend = False
    msg_type = message_analysis.type
    content = str_to_unicode(message_analysis.content)

    if (msg_type in (MSG_TYPE_TXT, MSG_TYPE_SYS) and content.find(u'现在可以开始聊天了') != -1) or (
            msg_type is MSG_TYPE_SYS and content.find(u'以上是打招呼的内容') != -1):
        # add friend
        is_add_friend = True
        user_username = message_analysis.real_talker
        bot_info = db.session.query(BotInfo).filter(BotInfo.username == message_analysis.username).first()
        if not bot_info:
            return is_add_friend
        a_contact = db.session.query(AContact).filter(AContact.username == user_username).first()
        logger.info(u"发现加bot好友用户. username: %s." % user_username)
        status, user_info = _bind_bot_success(a_contact.nickname, user_username, bot_info)
        we_conn = WechatConn()
        if status == SUCCESS:
            we_conn.send_txt_to_follower(
                "您好，欢迎使用数字货币友问币答！请将我拉入您要管理的区块链社群，拉入成功后即可为您的群提供实时查询币价，涨幅榜，币种成交榜，交易所榜，最新动态，行业百科等服务。步骤如下：\n拉我入群➡确认拉群成功➡ "
                "机器人在群发自我介绍帮助群友了解规则➡群友按照命令发关键字➡机器人回复➡完毕",
                user_info.open_id)
        else:
            EmailAlert.send_ue_alert(u"有用户尝试绑定机器人，但未绑定成功.疑似网络通信问题. "
                                     u"user_username: %s." % user_username)
    return is_add_friend


def _bind_bot_success(user_nickname, user_username, bot_info):
    """
    确认将一个bot绑入一个user之中
    :return:
    """

    # 因为AFriend等库更新未必在Message之前（在网速较慢的情况下可能出现）
    # 所以此处先sleep一段时间，等待AFriend更新后再读取
    # time.sleep(5)

    # 验证是否是好友
    a_friend = AFriend.get_a_friend(from_username = bot_info.username,
                                    to_username = user_username)
    if not a_friend:
        logger.error(u"好友信息出错. bot_username: %s. user_username: %s" %
                     (bot_info.username, user_username))
        return ERR_WRONG_ITEM, None

    if a_friend.type % 2 != 1:
        logger.error(u"用户与bot不是好友. bot_username: %s. user_username: %s" %
                     (bot_info.username, user_username))
        logger.info(u'但是放宽限制，暂时给予通过')
        # return ERR_WRONG_ITEM, None

    user_info_list = db.session.query(UserInfo).filter(UserInfo.nick_name == user_nickname).all()
    if len(user_info_list) > 1:
        logger.error(u"根据username无法确定其身份. bot_username: %s. user_username: %s" %
                     (bot_info.username, user_username))
        return ERR_HAVE_SAME_PEOPLE, None
    elif len(user_info_list) == 0:
        logger.error(u"配对user信息出错. bot_username: %s. user_username: %s" %
                     (bot_info.username, user_username))
        return ERR_WRONG_ITEM, None

    user_info_list_2 = db.session.query(UserInfo).filter(UserInfo.username == user_username).all()
    if user_info_list_2:
        logger.error(u"已绑定username与user关系. bot_username: %s. user_username: %s" %
                     (bot_info.username, user_username))
        return ERR_HAVE_SAME_PEOPLE, None

    user_info = user_info_list[0]
    user_info.username = user_username
    user_info.func_send_qun_messages = True
    user_info.func_auto_reply = False
    user_info.func_real_time_quotes = True
    user_info.func_synchronous_announcement = True
    user_info.func_coin_wallet = False
    db.session.merge(user_info)
    db.session.commit()
    logger.debug(u"完成绑定user与username关系. user_id: %s. username: %s." % (user_info.user_id, user_username))

    ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_info.user_id,
                                                          UserBotRelateInfo.bot_id == bot_info.bot_id).first()
    if not ubr_info:
        logger.error(u"没有完成bot与user的预绑定过程. user_id: %s." % user_info.user_id)
        return ERR_WRONG_ITEM, None

    ubr_info.is_setted = True
    ubr_info.is_being_used = True
    db.session.merge(ubr_info)
    db.session.commit()

    set_default_group(user_info)
    logger.info(u"已绑定bot与user关系. user_id: %s. bot_id: %s." % (user_info.user_id, bot_info.bot_id))
    return SUCCESS, user_info


def check_whether_message_is_add_friend_v2(message_analysis):
    """
    根据一条Message，返回是否为加bot为好友
    :return:
    """
    is_add_friend = False
    msg_type = message_analysis.type
    content = str_to_unicode(message_analysis.content)

    if message_analysis.is_to_friend and \
            ((msg_type in (MSG_TYPE_TXT, MSG_TYPE_SYS) and content.find(u'现在可以开始聊天了') != -1)
             or (msg_type is MSG_TYPE_SYS and content.find(u'以上是打招呼的内容') != -1)):
        # add friend
        is_add_friend = True
        # Mark
        # 考虑用启线程去处理
        _process_is_add_friend(message_analysis)

    return is_add_friend


def _process_is_add_friend(message_analysis):
    bot = db.session.query(BotInfo).filter(BotInfo.username == message_analysis.username).first()
    if not bot:
        logger.error(u"找不到 bot: " + str_to_unicode(message_analysis.username))
        return
    user_username = message_analysis.real_talker
    a_contact = AContact.get_a_contact(username = user_username)
    if a_contact:
        user_nickname = str_to_unicode(a_contact.nickname)
        logger.info(u"发现加bot好友用户. username: %s, nickname: %s" % (user_username, user_nickname))

        # 验证是否是唯一的friend
        a_friend = AFriend.get_a_friend(from_username = bot.username, to_username = user_username)
        if a_friend.type % 2 != 1:
            logger.error(u"好友信息出错. bot_username: %s. user_username: %s" %
                         (bot.username, user_username))
            return

        filter_list_user = UserInfo.get_filter_list(nickname = user_nickname)
        filter_list_user.append(UserInfo.username == u"")
        user_list = db.session.query(UserInfo).filter(*filter_list_user)\
            .order_by(UserInfo.create_time.desc()).all()
        if len(user_list) > 1:
            logger.error(u"根据username无法确定其身份. bot_username: %s. user_username: %s" %
                         (bot.username, user_username))
            return
        elif len(user_list) == 0:
            logger.error(u"配对user信息出错. bot_username: %s. user_username: %s" %
                         (bot.username, user_username))
            return

        user = user_list[0]
        user.username = user_username
        db.session.merge(user)

        ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user.user_id,
                                                              UserBotRelateInfo.bot_id == bot.bot_id).first()
        if not ubr_info:
            ubr_info = UserBotRelateInfo()
            ubr_info.preset_time = datetime.now()
            ubr_info.set_time = 0
        ubr_info.is_setted = True
        ubr_info.is_being_used = True
        db.session.merge(ubr_info)

        db.session.commit()
    else:
        logger.error(u"找不到 a_contact: " + str_to_unicode(user_username))


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
        logger.warning(u"无该username(%s)的qr_code." % str(username))
        return None
    img_str = base64.b64encode(f.read())
    f.close()
    return img_str
