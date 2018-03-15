# -*- coding: utf-8 -*-
import logging

from datetime import datetime

import copy

from configs.config import db, MSG_TYPE_TXT, MSG_TYPE_SYS, CONTENT_TYPE_TXT, CONTENT_TYPE_SYS, \
    USER_CHATROOM_R_PERMISSION_1
from models.android_db_models import AContact, AMember, AChatroomR, AFriend, AMessage
from models.chatroom_member_models import ChatroomInfo, BotChatroomR, UserChatroomR, ChatroomStatistic, \
    MemberStatistic, MemberInfo, ChatroomOverview
from models.user_bot_models import BotInfo, UserInfo, UserBotRelateInfo
from utils.u_time import get_today_0
from utils.u_transformat import str_to_unicode, unicode_to_str

logger = logging.getLogger("main")


class MessageAnalysis(db.Model):
    """
    用来存放将Message解析完成的结构，同时可以入库
    """
    __tablename__ = 'message_analysis'
    msg_id = db.Column(db.BigInteger, primary_key = True)
    msg_svr_id = db.Column(db.String(64), index = True, nullable = False)
    username = db.Column(db.String(32), index = True, nullable = False)

    type = db.Column(db.Integer, index = True, nullable = False)
    status = db.Column(db.Integer, index = True, nullable = False)
    is_send = db.Column(db.Boolean, index = True, nullable = False)
    talker = db.Column(db.String(32), index = True, nullable = False)
    content = db.Column(db.BLOB)
    img_path = db.Column(db.String(256))
    reserved = db.Column(db.BLOB)

    create_time = db.Column(db.DateTime, index = True, nullable = False)
    update_time = db.Column(db.TIMESTAMP, index = True, nullable = False)

    real_talker = db.Column(db.String(32), index = True, nullable = False)
    real_content = db.Column(db.BLOB)
    is_to_friend = db.Column(db.Boolean, index = True, nullable = False)
    is_at = db.Column(db.Boolean, index = True, nullable=False)
    member_id_be_at = db.Column(db.BigInteger, index=True, nullable=False)
    name_be_at = db.Column(db.String(64), index=True, nullable=False)

    # 预留字段，标记该 MSG 之后被赋予其他操作或者标记等
    is_handled = db.Column(db.Integer, index = True, nullable = False, default = 0)

    def __init__(self, a_msg):
        self.msg_id = a_msg.id
        self.msg_svr_id = a_msg.msg_svr_id
        self.username = a_msg.username
        self.type = a_msg.type
        self.status = a_msg.status
        self.is_send = a_msg.is_send
        self.talker = a_msg.talker
        self.content = a_msg.content
        self.img_path = a_msg.img_path
        self.reserved = a_msg.reserved
        self.create_time = a_msg.create_time
        self.is_at = False
        self.member_id_be_at = 0
        self.name_be_at = u""

    @staticmethod
    def analysis_and_save_a_message(a_message):
        """
        用于将a_message信息放入库中，并返回库中的结构模样
        :param a_message:
        :return:
        """
        if not isinstance(a_message, AMessage):
            # Mark
            # 几乎不报错，报错需要查错
            raise TypeError(u'AMessage Type Err')
        msg_ext = MessageAnalysis(a_message)
        content = str_to_unicode(msg_ext.content)
        is_send = msg_ext.is_send
        talker = msg_ext.talker
        msg_type = msg_ext.type

        # is_to_friend
        if msg_ext.talker.find(u'@chatroom') != -1:
            is_to_friend = False
        else:
            is_to_friend = True
        msg_ext.is_to_friend = is_to_friend

        # real_talker & real_content
        if is_to_friend or is_send or msg_type == MSG_TYPE_SYS:
            real_talker = talker
            real_content = content
        elif msg_type != MSG_TYPE_TXT:
            # 除了 TXT 和 SYS 的处理
            real_content = content
            if content.find(u':') == -1:
                # 收到的群消息没有 ':\n', "语言聊天已结束" 等
                real_talker = talker
            else:
                content_part = content.split(u':')
                real_talker = content_part[0]
        else:
            if content.find(u':\n') == -1:
                # Mark: 收到的群消息没有 ':\n'，需要查错
                logger.info(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(
                    msg_ext.msg_id) + u" type: " + unicode(msg_type))
                raise ValueError(u"ERR: chatroom msg received doesn't have ':\\n', msg_id: " + unicode(
                    msg_ext.msg_id) + u" type: " + unicode(msg_type))
            content_part = content.split(u':\n')
            real_talker = content_part[0]
            real_content = content_part[1]

        msg_ext.real_talker = real_talker
        msg_ext.real_content = unicode_to_str(real_content)

        return msg_ext

    @staticmethod
    def check_whether_message_is_add_friend(message_analysis):
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
            MessageAnalysis._process_is_add_friend(message_analysis)

        return is_add_friend

    @staticmethod
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

    @staticmethod
    def check_whether_message_is_add_qun(message_analysis):
        """
        根据一条Message，返回是否为加群，如果是，则完成加群动作
        :return:
        """
        is_add_qun = False
        msg_type = message_analysis.type
        content = str_to_unicode(message_analysis.content)

        if msg_type == MSG_TYPE_SYS and content.find(u'邀请你') != -1:
            is_add_qun = True
            MessageAnalysis._process_is_add_qun(message_analysis)

        return is_add_qun

    @staticmethod
    def _process_is_add_qun(message_analysis):
        content = str_to_unicode(message_analysis.content)
        bot_username = message_analysis.username
        bot = db.session.query(BotInfo).filter(BotInfo.username == bot_username).first()
        if not bot:
            logger.error(u"找不到 bot: " + str_to_unicode(message_analysis.username))
            return
        chatroomname = message_analysis.talker
        a_contact_chatroom = AContact.get_a_contact(username = chatroomname)
        if a_contact_chatroom:
            a_chatroom_r = AChatroomR.get_a_chatroom_r(chatroomname = chatroomname, username = bot.username)
            if not a_chatroom_r:
                a_chatroom_r = AChatroomR()
                a_chatroom_r.chatroomname = chatroomname
                a_chatroom_r.username = bot_username
                a_chatroom_r.create_time = datetime.now()
                db.session.add(a_chatroom_r)
                db.session.commit()
            user_nickname = content.split(u'邀请')[0][1:-1]
            if not user_nickname:
                logger.error(u"发现加群，但是获取不到邀请人 nickname, content: %s" % content)

            logger.info(u"发现加群. user_nickname: %s. chatroomname: %s." % (user_nickname, chatroomname))

            # 标记是否找到member_flag
            filter_list_a_member = AMember.get_filter_list(chatroomname = chatroomname, displayname = user_nickname,
                                                           is_deleted = 0)
            a_member_list = db.session.query(AMember).filter(*filter_list_a_member).all()
            if len(a_member_list) > 1:
                logger.error(u"一个群中出现两个相同的群备注名，无法确定身份. chatroomname: %s. user_nickname: %s." %
                             (chatroomname, user_nickname))
                return
            elif len(a_member_list) == 0:
                member_flag = False
            else:
                member_flag = True

            # 标记是否找到user_info
            user_list = db.session.query(UserInfo).filter(UserInfo.nick_name == user_nickname).all()
            if len(user_list) > 1:
                logger.error(u"根据nickname无法确定其身份. user_nickname: %s." % user_nickname)
                return
            elif len(user_list) == 0:
                user_flag = False
            else:
                user_flag = True

            if member_flag is True and user_flag is True:
                logger.error(u"同时匹配到群备注和用户昵称，无法识别用户身份. chatroomname: %s. user_nickname: %s." %
                             (chatroomname, user_nickname))
                return
            elif member_flag is False and user_flag is False:
                logger.error(u"没有找到群备注也没有找到用户昵称.没有找到该用户. chatroomname: %s. user_nickname: %s." %
                             (chatroomname, user_nickname))
                return
            elif user_flag is True:
                user = user_list[0]
            else:
                user = db.session.query(UserInfo).filter(UserInfo.username == a_member_list[0].username).first()
                if not user:
                    logger.error(u"没有找到对应的用户信息. user_username: %s." % a_member_list[0].username)
                    return
            user_id = user.user_id

            # chatroom
            chatroom = ChatroomInfo(chatroom_id = a_contact_chatroom.id, chatroomname = chatroomname,
                                    member_count = a_contact_chatroom.member_count).generate_create_time()
            db.session.merge(chatroom)

            # user_chatroom_r
            user_chatroom_r = UserChatroomR(user_id = user_id, chatroom_id = a_contact_chatroom.id,
                                            permission = USER_CHATROOM_R_PERMISSION_1)\
                .generate_create_time()
            db.session.add(user_chatroom_r)

            # bot_chatroom_r
            # 判断是否已经有 is_on 状态的其他 bot
            is_on = True
            bot_chatroom_r_is_on = db.session.query(BotChatroomR).filter(BotChatroomR.chatroomname == chatroomname,
                                                                         BotChatroomR.is_on == 1).first()
            if bot_chatroom_r_is_on:
                is_on = False
            bot_chatroom_r = BotChatroomR(a_chatroom_r_id = a_chatroom_r.id, chatroomname = a_chatroom_r.chatroomname,
                                          username = a_chatroom_r.username, is_on = is_on).generate_create_time()
            db.session.merge(bot_chatroom_r)

            # 初始化 MemberInfo 和 MemberOverview
            MemberInfo.update_members(chatroomname)

            # 初始化 ChatroomOverview
            ChatroomOverview.init_all_scope(chatroom_id = a_contact_chatroom.id)

            db.session.commit()
        else:
            logger.error(u"找不到 a_contact_chatroom: " + str_to_unicode(chatroomname))

    @staticmethod
    def check_is_removed(message_analysis):
        """
        根据一条Message，返回是否为被移除群聊，如果是，则完成相关动作
        :return:
        """

        is_removed = False
        msg_type = message_analysis.type
        content = str_to_unicode(message_analysis.content)
        if msg_type == MSG_TYPE_SYS and content.find(u'移出群聊') != -1:
            is_removed = True
            bot_username = message_analysis.username
            chatroomname = message_analysis.talker
            logger.info(u"发现机器人被踢出群聊. bot_username: %s. chatroomname: %s." % (bot_username, chatroomname))
            MessageAnalysis._process_is_removed(chatroomname, bot_username)
        return is_removed

    @staticmethod
    def _process_is_removed(chatroomname, username):
        filter_list_bcr = BotChatroomR.get_filter_list(chatroomname = chatroomname, username = username, is_on = True)
        bot_chatroom_r_list = db.session.query(BotChatroomR).filter(*filter_list_bcr).all()
        # 理论上只有一个
        for bcr in bot_chatroom_r_list:
            bcr.is_on = False

        db.session.commit()

    @staticmethod
    def check_whether_message_is_friend_into_qun(message_analysis):
        """
        根据一条message
        :param message_analysis:
        :return:
        """

    @staticmethod
    def count_msg(msg_id):
        msg = db.session.query(MessageAnalysis).filter(MessageAnalysis.msg_id == msg_id).first()
        if not msg:
            logger.error(u"message_analysis dose not exist: " + str(msg_id))
            return
        try:
            today = get_today_0()

            if msg.is_to_friend:
                pass
            else:
                content = str_to_unicode(msg.content)
                chatroomname = msg.talker
                username = msg.real_talker
                # is_send = msg.is_send
                msg_type = msg.type

                chatroom = db.session.query(ChatroomInfo).filter(ChatroomInfo.chatroomname == chatroomname).first()

                chatroom_id = chatroom.chatroom_id

                # calc chatroom statics
                logger.info('calc chatroom statistics')
                chatroom_statics = ChatroomStatistic.fetch_chatroom_statistics(chatroom_id = chatroom_id,
                                                                               time_to_day = today)
                logger.info('| speak_count')
                if msg_type != CONTENT_TYPE_SYS:
                    chatroom_statics.speak_count += 1
                    chatroom.total_speak_count += 1
                    member = MemberInfo.fetch_member_by_username(chatroomname, username)
                    if not member:
                        logger.error(u"find no member, chatroomname: %s, username: %s." % (chatroomname, username))
                        pass
                    talker_id = member.member_id

                    # calc member statics
                    logger.info('calc member   statistics')
                    member_statics = MemberStatistic.fetch_member_statistics(member_id = talker_id, time_to_day = today,
                                                                             chatroom_id = chatroom_id)
                    logger.info('| speak_count')
                    member_statics.speak_count += 1
                    member.speak_count += 1

                    if msg_type == CONTENT_TYPE_TXT:
                        if content.find(u'@') != -1:
                            logger.info('| be_at_count')
                            at_count = MessageAnalysis.extract_msg_be_at(msg, chatroom)
                            if msg.is_at:
                                chatroom_statics.at_count += at_count
                                chatroom.total_at_count += at_count

                db.session.commit()

                # content_type = CONTENT_TYPE_UNKNOWN
                # if msg_type == CONTENT_TYPE_TXT:
                #     content_type = CONTENT_TYPE_TXT
                # elif msg_type == CONTENT_TYPE_PIC:
                #     content_type = CONTENT_TYPE_PIC
                # elif msg_type == CONTENT_TYPE_MP3:
                #     content_type = CONTENT_TYPE_MP3
                # elif msg_type == CONTENT_TYPE_MP4:
                #     content_type = CONTENT_TYPE_MP4
                # elif msg_type == CONTENT_TYPE_GIF:
                #     content_type = CONTENT_TYPE_GIF
                # elif msg_type == CONTENT_TYPE_VIDEO:
                #     content_type = CONTENT_TYPE_VIDEO
                # elif msg_type == CONTENT_TYPE_SHARE:
                #     content_type = CONTENT_TYPE_SHARE
                # elif msg_type == CONTENT_TYPE_NAME_CARD:
                #     content_type = CONTENT_TYPE_NAME_CARD
                # elif msg_type == CONTENT_TYPE_SYS:
                #     content_type = CONTENT_TYPE_SYS
                #     # 红包
                #     if content == u'收到红包，请在手机上查看':
                #         logger.info(u'收到红包')
                #         content_type = CONTENT_TYPE_RED
                #     # 被邀请入群
                #     # Content="frank5433"邀请你和"秦思语-Doodod、磊"加入了群聊
                #     # "Sw-fQ"邀请你加入了群聊，群聊参与人还有：qiezi、Hugh、蒋郁、123
                #     elif content.find(u'邀请你') != -1:
                #         logger.info(u'invite_bot')
                #         MessageAnalysis.invite_bot(msg, chatroom)
                #
                #     # 其他人入群：邀请、扫码
                #     # "斗西"邀请"陈若曦"加入了群聊
                #     # " BILL"通过扫描"谢工@GitChat&图灵工作用"分享的二维码加入群聊
                #     # "風中落葉🍂"邀请"大冬天的、追忆那年的似水年华、往事随风去、搁浅、陈梁～HILTI"加入了群聊
                #     elif content.find(u'加入了群聊') != -1 or content.find(u'加入群聊') != -1:
                #         logger.info(u'invite_other')
                #         MessageAnalysis.invite_other(msg, chatroom)
                #
                #     # 修改群名
                #     # "阿紫"修改群名为“测试群”
                #     elif content.find(u'修改群名为') != -1:
                #         logger.info(u'修改群名')
                #         chatroom_nick_name = content.split(u'修改群名为')[1][1:-1]
                #         logger.info(u'chatroom_nick_name: ' + chatroom_nick_name)
                #         chatroom.nick_name = chatroom_nick_name
                #     # 移除群聊
                #     elif content.find(u'移除群聊') != -1:
                #         pass
                #     else:
                #         logger.info('UNKOWN SYS INFO: ')
                #         logger.info(content)
                #     db.session.commit()
                #
                # # calc content_type
                # logger.info('calc chatroom content type')
                # logger.info('calc member   content type')
                # chatroom_content_type = ChatroomContentType.get_chatroom_content_type(chatroom_id = chatroom_id,
                #                                                                       content_type = content_type)
                #
                # chatroom_content_type.incre()
                # if content_type is not CONTENT_TYPE_SYS and content_type is not CONTENT_TYPE_RED:
                #     member = db.session.query(Member).filter(Member.member_name == username).first()
                #     talker_id = member.id
                #     member_content_type = MemberContentType.get_member_content_type(member_id = talker_id,
                #                                                                     content_type = content_type)
                #     member_content_type.incre()
                #     if content_type is CONTENT_TYPE_SHARE:
                #         pass
                #
                # db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("Exception")
        finally:
            logger.info('count_msg db.session.close()')
            db.session.close()

    @staticmethod
    def extract_msg_be_at(msg, chatroom):
        at_count = 0
        content = str_to_unicode(msg.content)
        content_tmp = copy.deepcopy(content)
        today = get_today_0()
        member = db.session.query(MemberInfo).filter(MemberInfo.member_name == msg.real_talker).first()
        if not member:
            logger.error(u"找不到 member: " + str_to_unicode(msg.real_talker))
            return

        print u''
        chatroom_id = chatroom.chatroom_id
        if content_tmp.find(u'@') != -1:
            msg.is_at = True
            content_index = 0
            while content_tmp[content_index:].find(u'@') != -1:
                offset = content_index + content_tmp[content_index:].find(u'@') + 1
                end_index = 0
                if content_tmp[content_index:].find(u'\u2005') == -1:
                    content_tmp = content_tmp.replace(u' ', u'\u2005')
                    # print content_tmp.__repr__()
                while content_tmp[offset + end_index:].find(u'\u2005') != -1:
                    end_index += content_tmp[offset + end_index:].find(u'\u2005') + 1
                    name_be_at = content_tmp[offset:offset + end_index - 1]
                    if name_be_at == u'':
                        msg.is_at = False
                        break
                    if name_be_at.find(u'\u2005') != -1:
                        name_be_at = name_be_at.replace(u'\u2005', u' ')
                        print name_be_at.__repr__()
                    logger.debug(u'nick_name_be_at: ' + name_be_at)
                    member_be_at = MemberInfo.fetch_member_by_nickname(chatroomname = chatroom.chatroomname,
                                                                       nickname = name_be_at)
                    # 匹配到 member
                    if member_be_at:
                        msg.is_at = True
                        offset += end_index
                        logger.info(u'member_be_at ' + member_be_at.nickname)
                        member_be_at.be_at_count += 1
                        member_be_at_id = member_be_at.member_id
                        msg.member_id_be_at = member_be_at_id
                        msg.name_be_at = name_be_at
                        member_statics_be_at = MemberStatistic.fetch_member_statistics(member_id = member_be_at_id,
                                                                                       time_to_day = today,
                                                                                       chatroom_id = chatroom_id)
                        member_statics_be_at.be_at_count += 1

                        at_count += 1
                        break
                    else:
                        # logger.info(u'not find ' + name_be_at)
                        # 没有匹配到 member
                        # if not checked_flag:
                        #     # check
                        #     checked_flag = True
                        #     # check
                        #     MessageAnalysis.check_chatroom(chatroom)
                        #     end_index = 0
                        # else:
                        logger.info(u'really not find ' + name_be_at)
                content_index = offset
        return at_count

    # @staticmethod
    # def invite_bot(msg, chatroom):
    #     content = str_to_unicode(msg.content)
    #     content_tmp = copy.deepcopy(content)
    #     print u''
    #     chatroom_id = chatroom.id
    #     invitor_nick_name = content_tmp.split(u'邀请')[0][1:-1]
    #     logger.debug(u'invitor_nick_name: ' + invitor_nick_name)
    #
    #     invited_nick_name_list = list()
    #     if content_tmp.find(u'邀请你和') != -1:
    #         start_index = content_tmp.find(u'邀请你和')
    #         end_index = content_tmp.rfind(u'"加入')
    #         invited_nick_names = content_tmp[start_index + 5:end_index]
    #         invited_nick_name_list = invited_nick_names.split(u'、')
    #
    #     invitor = Member.get_member(chatroom_id = chatroom_id, nick_name = invitor_nick_name)
    #     if invitor:
    #         filter_list_wechat = Wechat.get_filter_list()
    #         filter_list_wechat.append(Wechat.nick_name == invitor.nick_name)
    #         filter_list_wechat.append(Wechat.sex == invitor.sex)
    #         filter_list_wechat.append(Wechat.city == invitor.city)
    #         filter_list_wechat.append(Wechat.province == invitor.province)
    #         invitor_wechat = db.session.query(Wechat).filter(*filter_list_wechat).first()
    #         if invitor_wechat:
    #             logger.info('invitor_wechat: ' + str(invitor_wechat.id))
    #             observer = Observer(wechat_id = invitor_wechat.id, chatroom_id = chatroom_id,
    #                                 is_on = True).generate_create_time()
    #             db.session.merge(observer)
    #         for invited_nick_name in invited_nick_name_list:
    #             logger.debug(u'invited_nick_name: ' + invited_nick_name)
    #             invited = Member.get_member(chatroom_id = chatroom_id, nick_name = invited_nick_name)
    #             times_tmp = 2
    #             while not invited and times_tmp > 0:
    #                 times_tmp -= 1
    #                 # check
    #                 MessageAnalysis.check_chatroom(chatroom)
    #                 invited = Member.get_member(chatroom_id = chatroom_id, nick_name = invited_nick_name)
    #             if invited:
    #                 m_i_m = MemberInviteMember(invitor_id = invitor.id, invited_id = invited.id,
    #                                            create_time = msg.create_time, invited_name = invited.nick_name,
    #                                            invitor_name = invitor.nick_name)
    #                 db.session.merge(m_i_m)
    #
    # @staticmethod
    # def invite_other(msg, chatroom):
    #     content = msg.content
    #     content_tmp = copy.deepcopy(content)
    #     print u''
    #     chatroom_id = chatroom.id
    #     # check
    #     MessageAnalysis.check_chatroom(chatroom)
    #     if content_tmp.find(u'邀请') != -1:
    #         invitor_nick_name = content_tmp.split(u'邀请')[0][1:-1]
    #         logger.debug(u'invitor_nick_name: ' + invitor_nick_name)
    #         # "斗西"邀请"陈若曦"加入了群聊
    #         # "風中落葉🍂"邀请"大冬天的、追忆那年的似水年华、往事随风去、搁浅、陈梁～HILTI"加入了群聊
    #         start_index = content_tmp.find(u'邀请')
    #         end_index = content_tmp.rfind(u'"加入')
    #         invited_nick_names = content_tmp[start_index + 3:end_index]
    #         invited_nick_name_list = invited_nick_names.split(u'、')
    #
    #     # " BILL"通过扫描"谢工@GitChat&图灵工作用"分享的二维码加入群聊
    #     elif content_tmp.find(u'通过扫描') != -1:
    #         nick_names = content_tmp.split(u'通过扫描')
    #         invited_nick_name = nick_names[0][2:-1]
    #         end_index = nick_names[1].rfind(u'"分享')
    #         invitor_nick_name = nick_names[1][1:end_index]
    #         logger.debug(u'invitor_nick_name: ' + invitor_nick_name)
    #         invited_nick_name_list = [invited_nick_name]
    #     else:
    #         logger.info(u'unknown invite type: ')
    #         logger.info(msg.content)
    #         return
    #
    #     invitor = Member.get_member(chatroom_id = chatroom_id, nick_name = invitor_nick_name)
    #     if invitor:
    #         for invited_nick_name in invited_nick_name_list:
    #             logger.debug(u'invited_nick_name: ' + invited_nick_name)
    #             invited = Member.get_member(chatroom_id = chatroom_id, nick_name = invited_nick_name)
    #             times_tmp = 2
    #             while not invited and times_tmp > 0:
    #                 times_tmp -= 1
    #                 # check
    #                 MessageAnalysis.check_chatroom(chatroom)
    #                 invited = Member.get_member(chatroom_id = chatroom_id, nick_name = invited_nick_name)
    #
    #             if invited:
    #                 m_i_m = MemberInviteMember(invitor_id = invitor.id, invited_id = invited.id,
    #                                            create_time = msg.create_time,
    #                                            invited_name = invited.nick_name,
    #                                            invitor_name = invitor.nick_name)
    #                 db.session.merge(m_i_m)
    #
    # @staticmethod
    # def check_chatroom(chatroom):
    #     bot = db.session.query(Bot).filter(Bot.id == chatroom.bot_id).first()
    #     a_contact_chatroom = db.session.query(AContact).filter(AContact.username == chatroom.chatroomname)
    #     chatroom = Chatroom().load_from_a_chatroom(
    #         bot_id = bot.id, a_contact_chatroom = a_contact_chatroom, wechat_id = chatroom.wechat_id) \
    #         .generate_create_time().generate_update_time()
    #     db.session.merge(chatroom)
    #     db.session.commit()
    #
    #     rows = db.session.query(AMember, AContact) \
    #         .outerjoin(AContact, AMember.username == AContact.username) \
    #         .filter(AMember.chatroomname == chatroom.chatroomname).all()
    #     chatroom.init_members_from_a_members(rows)
