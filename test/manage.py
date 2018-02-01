# -*- coding: utf-8 -*-

import unittest
import json

from configs.config import db
from core.qun_manage import set_default_group
from models.qun_friend import GroupInfo
from models.user_bot import UserInfo
from test.basic_default import get_a_default_test_user_info


class AddAGroupTestCase(unittest.TestCase):
    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()

        self.benchmark_token = 'g98jnrg3t9w'

        self.user_info = get_a_default_test_user_info()
        self.user_info.token = self.benchmark_token
        db.session.add(self.user_info)
        db.session.commit()

    def test_no_bot_info(self):
        set_default_group(self.user_info)

        json_data = {'token': self.benchmark_token, 'new_group_name': '新的测试分组'}
        json_data = json.dumps(json_data)
        self.app.post('/api/add_group', content_type="application/json", data=json_data)
        self.user_info = db.session.query(UserInfo).filter(UserInfo.token == self.benchmark_token).first()
        group_list = db.session.query(GroupInfo).filter(GroupInfo.user_id == self.user_info.user_id).all()
        self.assertEqual(len(group_list), 2)
        self.group_info = db.session.query(GroupInfo).filter(GroupInfo.user_id == self.user_info.user_id,
                                                             GroupInfo.is_default == 0).first()
        self.assertEqual(self.group_info.group_nickname, u'新的测试分组')

    def tearDown(self):
        self.user_info = db.session.query(UserInfo).filter(UserInfo.token == self.benchmark_token).first()
        group_list = db.session.query(GroupInfo).filter(GroupInfo.user_id == self.user_info.user_id).all()
        for group_info in group_list:
            db.session.delete(group_info)
        db.session.delete(self.user_info)
        db.session.commit()
