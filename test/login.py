# -*- coding: utf-8 -*-

import unittest

from datetime import datetime, timedelta


class CoreLoginTestCase(unittest.TestCase):
    def setUp(self):
        from core.user import UserLogin
        self.user_login = UserLogin(code='test')

    def test_generate_user_token(self):
        open_id_text = "sgvhniHsegvhnui"
        datetime_text = '2018-01-27 18:53:46.755942'
        token = self.user_login._generate_user_token(open_id=open_id_text, datetime_now=datetime_text)
        self.assertEqual('69b0b5ad44855e2963f9467d2edf68c6', token)


class VerifiedTokenTestCase(unittest.TestCase):
    def setUp(self):
        from models.user_bot import UserInfo
        user_info = UserInfo()

        user_info.open_id = "test_open_id"
        user_info.union_id = "test_union_id"

        user_info.nick_name = "test_nick_name"
        user_info.sex = 0
        user_info.province = "北京"
        user_info.city = "东城"
        user_info.country = "中国"
        user_info.avatar_url = "http://www.zheshiyigetest.com/123.jpg"

        user_info.code = "test_code"

        user_info.create_time = datetime.now()
        user_info.last_login_time = datetime.now()

        from core.user import UserLogin
        user_login = UserLogin(code='test')
        user_info.token = user_login._generate_user_token(open_id="sgvhniHsegvhnui", datetime_now=datetime.now())
        user_info.token_expired_time = datetime.now() + timedelta(days=2)

        user_info.func_send_qun_messages = False
        user_info.func_qun_sign = False
        user_info.func_auto_reply = False
        user_info.func_welcome_message = False

        from config import db
        db.session.add(user_info)
        db.session.commit()

    def test_valid_verified_token(self):
        pass
        # from core.user import UserLogin
        # verified_token = UserLogin().verify_token()

    def tearDown(self):
        from config import db
        from models.user_bot import UserInfo
        user_info = db.session.query(UserInfo).filter(UserInfo.code == "test_code").first()
        db.session.delete(user_info)
        db.session.commit()


class SandboxTestCase(unittest.TestCase):
    def setUp(self):
        import WinnerWinnerRobot

        WinnerWinnerRobot.app.config["TESTING"] = True
        self.app = WinnerWinnerRobot.app.test_client()

    def test_hello(self):
        rv = self.app.get("/hello")
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, "hello")


if __name__ == "__main__":
    unittest.main()
