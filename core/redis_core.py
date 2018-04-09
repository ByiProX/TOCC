# -*- coding: utf-8 -*-
import json
import logging

from configs.config import rds

logger = logging.getLogger('main')


def rds_lpush(chat_logs_type, msg_id, chatroomname, username, create_time, content):
    chat_logs = dict()
    chat_logs["type"] = chat_logs_type
    chat_logs["msg_id"] = msg_id
    chat_logs["chatroomname"] = chatroomname
    chat_logs["username"] = username
    chat_logs["time"] = create_time
    chat_logs["content"] = content
    rds.lpush("ct_logs", json.dumps(chat_logs))


if __name__ == '__main__':
    print 1
    # ct_logs
    print rds.keys()
    rds.delete("zclaiqcc1")
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
    pass
