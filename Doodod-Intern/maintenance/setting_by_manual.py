# -*- coding: utf-8 -*-
from datetime import datetime

from configs.config import db, SUCCESS
from core.qun_manage_core import set_default_group
from models.android_db_models import ABot, AFriend, AContact
# from models.material_library_models import MaterialLibraryDefault
# from models.real_time_quotes_models import RealTimeQuotesDefaultSettingInfo, RealTimeQuotesDefaultKeywordRelateInfo, \
#     RealTimeQuotesDefaultMaterialRelate
from models.message_ext_models import MessageAnalysis
from models.user_bot_models import BotInfo, UserInfo, UserBotRelateInfo
from utils.u_transformat import str_to_unicode, unicode_to_str


class SetBotRelSettingByManual:
    def __init__(self):
        pass

    @staticmethod
    def set_bot_info_by_a_bot_db():
        """
        当已经有新bot在ABot表中时，将BotInfo于ABot同步
        :return:
        """
        a_bot_list = db.session.query(ABot).all()
        bot_info_list = db.session.query(BotInfo).all()

        exist_bot_username_list = []
        for bot_info_iter in bot_info_list:
            exist_bot_username_list.append(bot_info_iter.username)

        for a_bot_iter in a_bot_list:
            if a_bot_iter.username in exist_bot_username_list:
                continue
            else:
                new_bot_info = BotInfo()
                new_bot_info.username = a_bot_iter.username
                new_bot_info.create_bot_time = datetime.now()
                new_bot_info.is_alive = True
                new_bot_info.alive_detect_time = datetime.now()
                db.session.add(new_bot_info)
                db.session.commit()
        return SUCCESS

    @staticmethod
    def bind_user_bot_relate_by_manual_confirmed(user_id):
        """
        自动去库中进行匹配，如果成功，则进行询问
        :param user_id:
        :return:
        """
        user_info = db.session.query(UserInfo).filter(UserInfo.user_id == user_id).first()
        if not user_info:
            raise ValueError("没有找到该用户基本信息")

        ubr_info_list = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_id).all()
        if len(ubr_info_list) > 1:
            raise ValueError("一个人不应该有多个关系绑定")
        if not ubr_info_list:
            raise ValueError("没有找到绑定关系，无法绑定")

        ubr_info = ubr_info_list[0]
        bot_id = ubr_info.bot_id

        if ubr_info.is_setted is True and ubr_info.is_being_used is True:
            print("用户已经绑定了bot")
            return 1

        bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == bot_id).first()
        if not bot_info:
            raise ValueError("已经绑定的关系不存在")
        bot_username = bot_info.username

        if not user_info.nick_name:
            print("用户信息中没有昵称，无法匹配")
            return -1

        aaa = unicode_to_str(user_info.nick_name)
        a_contact_list = db.session.query(AContact).filter(AContact.nickname == aaa).all()
        if not a_contact_list:
            print("没有找到该用户，无法匹配")
            return -2
        candidate_user_username = []
        for a_contact_iter in a_contact_list:
            user_username = a_contact_iter.username
            a_friend = db.session.query(AFriend).filter(AFriend.from_username == bot_username,
                                                        AFriend.to_username == user_username).first()
            if not a_friend:
                print("无好友")
                continue
            if a_friend.type % 2 != 1:
                print("有好友关系但不是好友")
                continue

            temp_dict = dict()
            temp_dict.setdefault("user_id", user_id)
            temp_dict.setdefault("user_nick_name", user_info.nick_name)
            temp_dict.setdefault("user_username", user_username)
            temp_dict.setdefault("bot_id", bot_id)
            temp_dict.setdefault("bot_username", bot_username)
            temp_dict.setdefault("conversation", [])
            ma_list = db.session.query(MessageAnalysis).filter(MessageAnalysis.username == bot_username,
                                                               MessageAnalysis.real_talker == user_username).order_by(
                MessageAnalysis.create_time.desc()).all()
            text_count = 0
            for ma_iter in ma_list:
                text = str_to_unicode(ma_iter.content)
                temp_dict['conversation'].append(text)
                text_count += 1
                if text_count > 5:
                    break

            candidate_user_username.append(temp_dict)

        print("-----------------------------------")
        for i, ti in enumerate(candidate_user_username):
            print(u"第%s个user" % (i + 1))
            print(u"用户id：" + unicode(ti['user_id']))
            print(u"用户昵称：" + ti['user_nick_name'])
            print(u"用户username：" + ti['user_username'])
            print(u"Bot id：" + unicode(ti['bot_id']))
            print(u"Bot username：" + ti['bot_username'])
            print(u"最近一些对话：")
            for ii, coti in enumerate(ti['conversation']):
                print(coti)
            print("-----------------------------------")
        res = raw_input("选择一个用户信息进行绑定:")
        res = int(res)
        if res <= 0:
            raise ValueError("用户id过小")
        res = int(res) - 1
        if res >= len(candidate_user_username):
            raise ValueError("用户过大")
        print(u"选择了第%s个用户 %s." % (res + 1, candidate_user_username[res]['user_nick_name']))

        # 开始更新各个方面
        user_info.username = candidate_user_username[res]['user_username']
        user_info.func_send_qun_messages = True
        user_info.func_auto_reply = False
        user_info.func_real_time_quotes = True
        user_info.func_synchronous_announcement = True
        user_info.func_coin_wallet = False
        db.session.merge(user_info)

        ubr_info.is_setted = True
        ubr_info.is_being_used = True
        db.session.merge(ubr_info)
        db.session.commit()

        set_default_group(user_info)
        print("已绑定bot与user关系")
        return 0

    @staticmethod
    def bind_user_bot_relate(user_id, user_username, check_nick_name=True):
        """
        绑定一个存在user-bot关系的user
        确认其与bot为好友后，绑定其关系
        :return:
        """
        user_info = db.session.query(UserInfo).filter(UserInfo.user_id == user_id).first()
        if not user_info:
            raise ValueError("没有找到该用户基本信息")

        ubr_info_list = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id == user_id).all()
        if len(ubr_info_list) > 1:
            raise ValueError("一个人不应该有多个关系绑定")
        if not ubr_info_list:
            raise ValueError("没有找到绑定关系，无法绑定")

        ubr_info = ubr_info_list[0]
        bot_id = ubr_info.bot_id

        bot_info = db.session.query(BotInfo).filter(BotInfo.bot_id == bot_id).first()
        if not bot_info:
            raise ValueError("已经绑定的关系不存在")
        bot_username = bot_info.username

        a_friend = db.session.query(AFriend).filter(AFriend.from_username == bot_username,
                                                    AFriend.to_username == user_username).first()

        if not a_friend:
            print("该用户没有与其对应的bot有任何关系")
            return -1
        if a_friend.type % 2 != 1:
            print("用用户与其对应的bot不是好友")
            return -2

        a_contact = db.session.query(AContact).filter(AContact.username == user_username).first()

        if not a_contact:
            print("contact表中没有该用户的基本信息")
            return -3
        if check_nick_name:
            if not a_contact.nickname:
                print("contact表中没有用户的nickname，无法确认关系")
                return -4
        if check_nick_name:
            if a_contact.nickname != user_info.nick_name:
                print("用户的安卓端昵称与微信返回昵称无法匹配")
                return -5

        # 开始更新各个方面
        user_info.username = user_username
        user_info.func_send_qun_messages = True
        user_info.func_auto_reply = False
        user_info.func_real_time_quotes = True
        user_info.func_synchronous_announcement = True
        user_info.func_coin_wallet = False
        db.session.merge(user_info)

        ubr_info.is_setted = True
        ubr_info.is_being_used = True
        db.session.merge(ubr_info)
        db.session.commit()

        set_default_group(user_info)
        print("已绑定bot与user关系")
        return 0


class SetRealTimeQuoteSettingByManual:
    def __init__(self):
        pass

    @staticmethod
    def set_a_coin_setting_just_one_text(keyword_list, one_text):
        """
        老版代码，现在数据库格式已经更改
        """
        raise NotImplementedError
        # now_time = datetime.now()
        # rt_quotes_ds_info = RealTimeQuotesDefaultSettingInfo()
        # rt_quotes_ds_info.create_time = now_time
        # db.session.add(rt_quotes_ds_info)
        # db.session.commit()
        #
        # ds_id = rt_quotes_ds_info.ds_id
        #
        # # 存入关键词
        # for i, keyword in enumerate(keyword_list):
        #     rt_quotes_dkr_info = RealTimeQuotesDefaultKeywordRelateInfo()
        #     rt_quotes_dkr_info.ds_id = ds_id
        #     rt_quotes_dkr_info.keyword = keyword
        #     rt_quotes_dkr_info.is_full_match = True
        #     rt_quotes_dkr_info.send_seq = i
        #     db.session.add(rt_quotes_dkr_info)
        # db.session.commit()
        #
        # # 新建默认模板
        # mld_info = MaterialLibraryDefault()
        # # 文字类型
        # mld_info.task_send_type = 1
        # mld_info.task_send_content = {"text": one_text}
        # mld_info.used_count = 0
        # mld_info.create_time = now_time
        # mld_info.last_used_time = now_time
        # db.session.add(mld_info)
        # db.session.commit()
        #
        # dm_id = mld_info.dm_id
        #
        # # 存入物料关系
        # rt_quotes_ds_ml_rel = RealTimeQuotesDefaultMaterialRelate()
        # rt_quotes_ds_ml_rel.ds_id = ds_id
        # rt_quotes_ds_ml_rel.dm_id = dm_id
        # rt_quotes_ds_ml_rel.send_seq = 0
        # db.session.add(rt_quotes_ds_ml_rel)
        # db.session.commit()


if __name__ == '__main__':
    SetBotRelSettingByManual.bind_user_bot_relate_by_manual_confirmed(44)