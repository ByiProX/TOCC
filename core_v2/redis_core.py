# -*- coding: utf-8 -*-
import json
import logging

from configs.config import rds

logger = logging.getLogger('main')


def rds_lpush(chat_logs_type, msg_id, chatroomname = None, username = None, create_time = None, content = None, err = False):
    chat_logs = dict()
    chat_logs["type"] = chat_logs_type
    chat_logs["msg_id"] = msg_id
    if err:
        queue_name = "ct_logs_err"
    else:
        chat_logs["chatroomname"] = chatroomname
        chat_logs["username"] = username
        chat_logs["time"] = create_time
        chat_logs["content"] = content
        queue_name = "ct_logs"
    rds.lpush(queue_name, json.dumps(chat_logs))


if __name__ == '__main__':
    print 1
    # ct_logs
    # print rds.keys()
    # rds.delete("zclaiqcc1")
    # rds.lpush("zclaiqcc1", 1)
    # rds.lpush("zclaiqcc1", "2")
    # rds.lpush("zclaiqcc1", [3, 4])
    # rds.lpush("zclaiqcc1", {"5": 6})
    # rds.lpush("zclaiqcc1", {"7": [8]})
    # d = rds.dump("zclaiqcc1")
    # print rds.rpop("zclaiqcc1")
    # print rds.rpop("zclaiqcc1")
    # print rds.rpop("zclaiqcc1")
    # print rds.rpop("zclaiqcc1")
    # print rds.rpop("zclaiqcc1")
    # while True:
    #     print rds.get("zclaiqcc1")
    pass
