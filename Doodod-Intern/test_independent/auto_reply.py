# -*- coding: utf-8 -*-
import json

from datetime import datetime

import requests
import unittest
from configs.test_config import test_db
from models.user_bot_models import UserInfo


# class CreateAutoReplySettingTestCase(unittest.TestCase):
#     def test_main(self):
#         json_data = {
#             "token": "test_token_123",
#             "chatroom_list": [
#                 1
#             ],
#             "message_list": [
#                 {
#                     "send_type": 1,
#                     "text": "感谢购买该公开课~谢谢~谢谢~"
#                 }
#             ],
#             "keyword_list": [
#                 {
#                     "keyword_content": "公开课",
#                     "is_full_match": True
#                 },
#                 {
#                     "keyword_content": "运营",
#                     "is_full_match": True
#                 }
#             ]
#         }
#         r = requests.post("http://127.0.0.1:5500/winner_api/create_a_auto_reply_setting", json=json_data)
#         print(r.content)

# class SwitchFuncAutoReplyTestCase(unittest.TestCase):
#     def test_open(self):
#         json_data = {
#             "token": "test_token_123",
#             "switch": True
#         }
#         r = requests.post("http://127.0.0.1:5500/winner_api/switch_func_auto_reply", json=json_data)
#         print(r.content)
#
#     def test_close(self):
#         json_data = {
#             "token": "test_token_123",
#             "switch": False
#         }
#         r = requests.post("http://127.0.0.1:5500/winner_api/switch_func_auto_reply", json=json_data)
#         print(r.content)

# class GetAutoReplySettingTestCase(unittest.TestCase):
#     def test_main(self):
#         json_data = {
#                         "token": "test_token_123",
#                     }
#         r = requests.post("http://127.0.0.1:5500/winner_api/get_auto_reply_setting", json=json_data)
#         print(r.content)

class DeleteAutoReplySettingTestCase(unittest.TestCase):
    def test_main(self):
        json_data = {
            "token": "test_token_123",
            "setting_id":1
        }
        r = requests.post("http://127.0.0.1:5500/winner_api/delete_a_auto_reply_setting", json=json_data)
        print(r.content)


if __name__ == "__main__":
    unittest.main()
