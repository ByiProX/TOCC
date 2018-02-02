# -*- coding: utf-8 -*-

from configs.config import db


class MessageAnalysis(db.Model):
    """
    用来存放将Message解析完成的结构，同时可以入库
    """
    __tablename__ = 'message_analysis'
    msg_id = db.Column(db.BigInteger, primary_key = True)
    msg_svr_id = db.Column(db.String(64), index = True, nullable = False)
    username = db.Column(db.String(32), index = True, nullable = False)

    type = db.Column(db.Integer, index = True, nullable = False)
    status = db.Column(db.Integer, index = True, nullable = False)
    is_send = db.Column(db.Boolean, index = True, nullable = False)
    talker = db.Column(db.String(32), index = True, nullable = False)
    content = db.Column(db.BLOB)
    img_path = db.Column(db.String(256))
    reserved = db.Column(db.BLOB)

    create_time = db.Column(db.DateTime, index = True, nullable = False)
    update_time = db.Column(db.TIMESTAMP, index = True, nullable = False)

    real_talker = db.Column(db.String(32), index = True, nullable = False)
    real_content = db.Column(db.BLOB)
    is_to_friend = db.Column(db.Boolean, index = True, nullable = False)

    # 预留字段，标记该 MSG 之后被赋予其他操作或者标记等
    is_handled = db.Column(db.Integer, index = True, nullable = False, default = 0)

    def __init__(self, a_msg):
        self.msg_id = a_msg.id
        self.msg_svr_id = a_msg.msg_svr_id
        self.username = a_msg.username
        self.type = a_msg.type
        self.status = a_msg.status
        self.is_send = a_msg.is_send
        self.talker = a_msg.talker
        self.content = a_msg.content
        self.img_path = a_msg.img_path
        self.reserved = a_msg.reserved
        self.create_time = a_msg.create_time
