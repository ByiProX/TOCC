# -*- coding: utf-8 -*-

"""
原本准备将所有的内容都放入一起来写，但是后来发现不行
"""

import unittest
import json

from datetime import datetime

from core.qun_manage_core import set_default_group
from core.user_core import _bind_bot_success, _get_qr_code_base64_str
from models.android_db_models import ABot, AFriend
from models.qun_friend_models import GroupInfo
from models.user_bot_models import UserBotRelateInfo, UserInfo, BotInfo
from test.basic_default import get_a_default_test_user_info, get_a_default_test_bot_info, get_a_default_test_a_bot, \
    get_a_default_test_a_contact, create_a_new_app


class TestGenerateUserTokenTestCase(unittest.TestCase):
    """
    测试token生成
    """

    def setUp(self):
        from core.user_core import UserLogin
        self.user_login = UserLogin(code='test')

    def test_generate_user_token(self):
        open_id_text = "sgvhniHsegvhnui"
        datetime_text = '2018-01-27 18:53:46.755942'
        token = self.user_login._generate_user_token(open_id=open_id_text, datetime_now=datetime_text)
        self.assertEqual('69b0b5ad44855e2963f9467d2edf68c6', token)


class LoginAndManageTestCase(unittest.TestCase):
    """
    从头到尾测试一遍流程，然后再把所有相关库清空
    """

    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()
        self.db = create_a_new_app()

        self.benchmark_code = 'aigibwg'
        self.benchmark_token = 'g98jnrg3t9w'
        self.user_nick_name = '测试账号'

        self.user_info = get_a_default_test_user_info()
        self.user_info.code = self.benchmark_code
        self.user_info.token = self.benchmark_token
        self.user_info.nick_name = self.user_nick_name
        self.db.session.add(self.user_info)
        self.db.session.commit()

    def test_login_and_manage(self):
        # 测试code进入接口
        json_data = {'code': self.benchmark_code}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/verify_code', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        token = res_data.get('content').get('user_info').get('token')
        self.assertEqual(token, self.benchmark_token)

        # 测试错误token
        json_data = {'token': 'atyn4iytv4'}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/get_user_basic_info', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        err_code = res_data['err_code']
        self.assertEqual(err_code, -4)

        # 测试未绑定时的状态
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

        # 测试分配机器人并设置全局昵称
        json_data = {'token': self.benchmark_token, 'bot_nickname': 'test_bot_nickname'}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/initial_robot_nickname', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        content = res_data['content']
        # 因为测试设置地址问题，该读取无法读取到qr_code的图片

        # 分配后直接调用全数据
        json_data = {'token': self.benchmark_token}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/get_user_basic_info', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        content = res_data['content']
        bot_info = content['bot_info']
        user_func = content['user_func']
        total_info = content['total_info']
        self.assertTrue(bot_info['bot_status'])
        self.assertEqual(user_func['func_send_messages'], False)
        self.assertEqual(user_func['func_sign'], False)
        self.assertEqual(user_func['func_reply'], False)
        self.assertEqual(user_func['func_welcome'], False)
        self.assertEqual(total_info['qun_count'], 0)
        self.assertEqual(total_info['cover_member_count'], 0)

        # 模拟绑定群的操作
        self.user_info = self.db.session.query(UserInfo).filter(UserInfo.token == self.benchmark_token).first()
        self.ubr_info = self.db.session.query(UserBotRelateInfo).filter(
            UserBotRelateInfo.user_id == self.user_info.user_id).first()
        self.bot_info = self.db.session.query(BotInfo).filter(BotInfo.bot_id == self.ubr_info.bot_id).first()
        a_friend = AFriend()
        a_friend.from_username = self.bot_info.username
        a_friend.to_username = "temp_usernamesdorhu"
        a_friend.create_time = datetime.now()
        a_friend.update_time = datetime.now()
        self.db.session.add(a_friend)
        self.db.session.commit()

        _bind_bot_success(self.user_info.nick_name, "temp_usernamesdorhu", self.bot_info)

        json_data = {'token': self.benchmark_token}
        json_data = json.dumps(json_data)
        rv = self.app.post('/api/get_group_list', content_type="application/json", data=json_data)
        res_data = json.loads(rv.data)
        content = res_data['content']
        raise NotImplementedError
