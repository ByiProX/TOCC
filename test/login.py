# -*- coding: utf-8 -*-

import unittest

from core.user import UserLogin


class CoreLoginTestCase(unittest.TestCase):
    def setUp(self):
        self.user_login = UserLogin(code='test')

    def test_generate_user_token(self):
        token = self.user_login._generate_user_token()
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 32)


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
