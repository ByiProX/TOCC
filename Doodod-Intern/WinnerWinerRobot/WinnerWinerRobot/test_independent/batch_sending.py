# -*- coding: utf-8 -*-
import json

from datetime import datetime

import requests
import unittest
from configs.test_config import test_db
from models.user_bot_models import UserInfo


class CreateASendingTaskTestCase(unittest.TestCase):
    def test_main_pro(self):
        json_data = {
            "token": "test_token_123",
            "chatroom_list": [
                1
            ],
            "message_list": [
                {
                    "send_type": 1,
                    "text": "大家好，感谢大家购买这个公开课"
                }
            ]
        }
        r = requests.post("http://127.0.0.1:5500/api/create_a_sending_task", json=json_data)
        print(r.content)

class GetTaskInfoTestCase(unittest.TestCase):
    def test_main_pro(self):
        json_data = {
            "token": "test_token_123",
            "sending_task_id": 1
        }
        r = requests.post("http://127.0.0.1:5500/api/get_task_detail", json=json_data)
        print(r.content)

class GetBatchSendingTaskTestCase(unittest.TestCase):
    def test_main_pro(self):
        json_data = {
            "token": "test_token_123"
        }
        r = requests.post("http://127.0.0.1:5500/api/get_batch_sending_task", json=json_data)
        print(r.content)

if __name__ == "__main__":
    unittest.main()
