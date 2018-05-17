# -*- coding: utf-8 -*-
import json

from datetime import datetime

import requests
import unittest
from configs.test_config import test_db
from models.user_bot_models import UserInfo


class VerifyCodeTestCase(unittest.TestCase):
    def test_empty(self):
        r = requests.post("http://127.0.0.1:5500/api/verify_code")
        self.assertEqual(r.status_code, 200)

    def test_code(self):
        sample = test_db.session.query(UserInfo).first()
        if not isinstance(sample, UserInfo):
            raise TypeError
        if not sample:
            raise EnvironmentError

        json_data = {"code": sample.code}
        r = requests.post("http://127.0.0.1:5500/api/verify_code", json=json_data)
        c = json.loads(r.content)
        c = c['content']
        self.assertEqual(c["user_info"]["user_id"], sample.user_id)
        now_time = datetime.now()
        self.assertGreater(sample.token_expired_time, now_time)


if __name__ == "__main__":
    unittest.main()
