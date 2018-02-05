# -*- coding: utf-8 -*-
import json

import time

import requests
import unittest
from configs.test_config import test_db
from models.qun_friend_models import GroupInfo
from models.user_bot_models import UserInfo


class AddAGroupTestCase(unittest.TestCase):
    def test_long_name(self):
        sample = test_db.session.query(UserInfo).first()
        if not isinstance(sample, UserInfo):
            raise TypeError
        if not sample:
            raise EnvironmentError

        json_data = {"token": sample.token, "new_group_name": "在这里起一个长度为十七个字符的名字"}
        r = requests.post("http://127.0.0.1:5500/api/add_group", json=json_data)
        c = json.loads(r.content)
        c = c['err_code']
        self.assertEqual(c, -14)

    def test_add_group(self):
        sample = test_db.session.query(UserInfo).first()
        if not isinstance(sample, UserInfo):
            raise TypeError
        if not sample:
            raise EnvironmentError

        gi = test_db.session.query(GroupInfo).filter(GroupInfo.user_id == sample.user_id).all()
        now_count = len(gi)

        json_data = {"token": sample.token, "new_group_name": "普通的测试名字"}
        r = requests.post("http://127.0.0.1:5500/api/add_group", json=json_data)
        c = json.loads(r.content)
        c = c['err_code']
        self.assertEqual(c, 0)
        c = json.loads(r.content)['content']
        group_id = c['group']['group_id']

        #FIXME 不知道为什么读不到正确的结果
        gi2 = test_db.session.query(GroupInfo).filter(GroupInfo.group_id == group_id).first()
        self.assertEqual(now_count, len(gi2))

        gi3 = test_db.session.query(GroupInfo).filter(GroupInfo.group_nickname == "普通的测试名字",
                                                      GroupInfo.user_id == sample.user_id).first()
        self.assertIsNotNone(gi3)
        test_db.session.delete(gi3)
        test_db.session.commit()
        gi4 = test_db.session.query(GroupInfo).filter(GroupInfo.user_id == sample.user_id).all()
        self.assertEqual(now_count, len(gi4))


if __name__ == "__main__":
    unittest.main()
