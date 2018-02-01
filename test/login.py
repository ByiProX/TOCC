# -*- coding: utf-8 -*-

import unittest
import json

from core.qun_manage import set_default_group
from core.user import _bind_bot_success
from models.android_db import ABot
from models.qun_friend import GroupInfo
from models.user_bot import UserBotRelateInfo, UserInfo
from test.basic_default import get_a_default_test_user_info, get_a_default_test_bot_info, get_a_default_test_a_bot, \
    get_a_default_test_a_contact, create_a_new_app


class CoreLoginTestCase(unittest.TestCase):
    def setUp(self):
        from core.user import UserLogin
        self.user_login = UserLogin(code='test')

    def test_generate_user_token(self):
        open_id_text = "sgvhniHsegvhnui"
        datetime_text = '2018-01-27 18:53:46.755942'
        token = self.user_login._generate_user_token(open_id=open_id_text, datetime_now=datetime_text)
        self.assertEqual('69b0b5ad44855e2963f9467d2edf68c6', token)


class VerifyCodeTestCase(unittest.TestCase):
    """
    测试code在库中，但是微信并不认可的逻辑
    """

    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()
        self.db = create_a_new_app()

        self.benchmark_code = 'aigibwg'
        self.benchmark_token = 'g98jnrg3t9w'

        self.user_info = get_a_default_test_user_info()
        self.user_info.code = self.benchmark_code
        self.user_info.token = self.benchmark_token
        self.db.session.add(self.user_info)
        self.db.session.commit()

    def test_valid(self):
        json_data = {'code': self.benchmark_code}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/verify_code', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        token = res_data.get('content').get('user_info').get('token')
        self.assertEqual(token, self.benchmark_token)

    def tearDown(self):
        self.db.session.delete(self.user_info)
        self.db.session.commit()


class VerifyTokenInfoTestCase(unittest.TestCase):
    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()
        self.db = create_a_new_app()

        self.benchmark_token = 'g98jnrg3t9w'

        self.user_info = get_a_default_test_user_info()
        self.user_info.token = self.benchmark_token
        self.db.session.add(self.user_info)
        self.db.session.commit()

    def test_no_bot_info(self):
        json_data = {'token': 'atyn4iytv4'}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/get_user_basic_info', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        err_code = res_data['err_code']
        self.assertEqual(err_code, -4)

    def tearDown(self):
        self.db.session.delete(self.user_info)
        self.db.session.commit()


class UserBasicInfoNoBotInfoTestCase(unittest.TestCase):
    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()
        self.db = create_a_new_app()

        self.benchmark_token = 'g98jnrg3t9w'

        self.user_info = get_a_default_test_user_info()
        self.user_info.token = self.benchmark_token
        self.db.session.add(self.user_info)
        self.db.session.commit()

    def test_no_bot_info(self):
        json_data = {'token': self.benchmark_token}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/get_user_basic_info', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        content = res_data['content']
        bot_info = content['bot_info']
        user_func = content['user_func']
        total_info = content['total_info']
        self.assertEqual(bot_info, None)
        self.assertEqual(user_func['func_send_messages'], False)
        self.assertEqual(user_func['func_sign'], False)
        self.assertEqual(user_func['func_reply'], False)
        self.assertEqual(user_func['func_welcome'], False)
        self.assertEqual(total_info['qun_count'], 0)
        self.assertEqual(total_info['cover_member_count'], 0)

    def tearDown(self):
        self.db.session.delete(self.user_info)
        self.db.session.commit()


class InitialRobotNameTestCase(unittest.TestCase):
    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()
        self.db = create_a_new_app()

        self.benchmark_token = 'g98jnrg3t9w'

        self.user_info = get_a_default_test_user_info()
        self.user_info.token = self.benchmark_token

        self.bot_info = get_a_default_test_bot_info()

        self.db.session.add(self.bot_info)
        self.db.session.add(self.user_info)
        self.db.session.commit()

    def test_initial_robot_nickname(self):
        json_data = {'token': self.benchmark_token, 'bot_nickname': 'test_bot_nickname'}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/initial_robot_nickname', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        content = res_data['content']
        qr_code = content['qr_code']
        self.assertEqual(qr_code, 'http:')

        self.ubr_info = self.db.session.query(UserBotRelateInfo). \
            filter(UserBotRelateInfo.user_id == self.user_info.user_id,
                   UserBotRelateInfo.bot_id == self.bot_info.bot_id).first()
        self.assertEqual(self.ubr_info.chatbot_default_nickname, 'test_bot_nickname')

    def tearDown(self):
        self.db.session.delete(self.ubr_info)
        self.db.session.delete(self.bot_info)
        self.db.session.delete(self.user_info)
        self.db.session.commit()


class UserBasicInfoAllInfoTestCase(unittest.TestCase):
    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()
        self.db = create_a_new_app()

        self.benchmark_token = 'g98jnrg3t9w'

        self.user_info = get_a_default_test_user_info()
        self.user_info.token = self.benchmark_token

        self.bot_info = get_a_default_test_bot_info()

        self.a_bot_test = get_a_default_test_a_bot()

        self.db.session.add(self.bot_info)
        self.db.session.add(self.user_info)
        self.db.session.add(self.a_bot_test)
        self.db.session.commit()

    def test_all_info(self):
        # 调用initial接口创建ubr关系
        json_data = {'token': self.benchmark_token, 'bot_nickname': 'test_bot_nickname'}
        json_data = json.dumps(json_data)
        self.app.post('/api/initial_robot_nickname', content_type="application/json", data=json_data)
        self.ubr_info = self.db.session.query(UserBotRelateInfo). \
            filter(UserBotRelateInfo.user_id == self.user_info.user_id,
                   UserBotRelateInfo.bot_id == self.bot_info.bot_id).first()

        json_data = {'token': self.benchmark_token}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/get_user_basic_info', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        content = res_data['content']
        bot_info = content['bot_info']
        user_func = content['user_func']
        total_info = content['total_info']
        self.assertEqual(bot_info['bot_id'], self.bot_info.bot_id)
        self.assertEqual(bot_info['chatbot_nickname'], self.ubr_info.chatbot_default_nickname)
        self.assertTrue(bot_info['bot_status'])
        self.a_bot_test = self.db.session.query(ABot).filter(ABot.username == self.bot_info.username).first()
        self.assertEqual(bot_info['bot_avatar'], self.a_bot_test.avatar_url2)
        self.assertEqual(bot_info['bot_qr_code'], self.bot_info.qr_code)
        self.assertEqual(user_func['func_send_messages'], False)
        self.assertEqual(user_func['func_sign'], False)
        self.assertEqual(user_func['func_reply'], False)
        self.assertEqual(user_func['func_welcome'], False)
        self.assertEqual(total_info['qun_count'], 0)
        self.assertEqual(total_info['cover_member_count'], 0)

    def tearDown(self):
        self.db.session.delete(self.ubr_info)
        self.db.session.delete(self.bot_info)
        self.db.session.delete(self.user_info)
        self.db.session.delete(self.a_bot_test)
        self.db.session.commit()


class GetBalancedBotTestCase(unittest.TestCase):
    pass


class SetDefaultGroupTestCase(unittest.TestCase):
    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()
        self.db = create_a_new_app()

        self.benchmark_token = 'g98jnrg3t9w'

        self.user_info = get_a_default_test_user_info()
        self.user_info.token = self.benchmark_token

        self.db.session.add(self.user_info)
        self.db.session.commit()

    def test_set_default_group(self):
        set_default_group(self.user_info)
        group_list = self.db.session.query(GroupInfo).filter(GroupInfo.user_id == self.user_info.user_id).all()
        self.assertEqual(len(group_list), 1)

        self.group_info = group_list[0]
        self.assertTrue(self.group_info.is_default)
        self.assertEqual(self.group_info.group_nickname, u'未分组')

    def tearDown(self):
        self.db.session.delete(self.group_info)
        self.db.session.delete(self.user_info)
        self.db.session.commit()


# class BindBotSuccessCoreTestCase(unittest.TestCase):
#     def setUp(self):
#         import WinnerWinnerRobot
#
#         WinnerWinnerRobot.app.config["TESTING"] = True
#         self.app = WinnerWinnerRobot.app.test_client()
#         self.db = create_a_new_app(self.app)
#
#         self.benchmark_token = 'g98jnrg3t9w'
#
#         self.user_info = get_a_default_test_user_info()
#         self.user_info.nick_name = '测试账号_afksb'
#         self.user_info.token = self.benchmark_token
#
#         self.bot_info = get_a_default_test_bot_info()
#
#         self.a_bot_test = get_a_default_test_a_bot()
#         self.a_contact = get_a_default_test_a_contact()
#
#         db.session.add(self.bot_info)
#         db.session.add(self.user_info)
#         db.session.add(self.a_bot_test)
#         db.session.add(self.a_contact)
#         db.session.commit()
#
#     def test_bind_bot_success(self):
#         # 初始化
#         json_data = {'token': self.benchmark_token, 'bot_nickname': 'test_bot_nickname'}
#         json_data = json.dumps(json_data)
#         self.app.post('/api/initial_robot_nickname', content_type="application/json", data=json_data)
#
#         _bind_bot_success('测试账号_afksb', 'test_user_username', self.bot_info)
#
#         self.assertEqual(self.user_info.username,'test_user_username')
#
#         ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id).all()
#         self.assertEqual(len(ubr_info),1)
#         ubr_info = ubr_info[1]
#         self.assertEqual(ubr_info.bot_id,self.bot_info.bot_id)
#         self.assertTrue(ubr_info.is_setted)
#         self.assertTrue(ubr_info.is_being_used)
#
#     def tearDown(self):
#         db.session.delete(self.bot_info)
#         db.session.delete(self.user_info)
#         db.session.delete(self.a_bot_test)
#         db.session.delete(self.a_contact)
#         ubr_info = db.session.query(UserBotRelateInfo).filter(UserBotRelateInfo.user_id).first()
#         db.session.delete(ubr_info)
#         db.session.commit()

if __name__ == "__main__":
    unittest.main()
