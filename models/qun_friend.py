# -*- coding: utf-8 -*-

from config import db
from utils.u_model_json_str import model_to_dict


class GroupInfo(db.Model):
    """
    一个User可以有多个Group，一个Group只可以给一个人
    """
    __tablename__ = "group_name"
    group_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    group_nickname = db.Column(db.String(32), index=True, nullable=False)

    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    user_group_seq = db.Column(db.Integer, index=True, nullable=True)

    create_time = db.Column(db.DateTime, index=True, nullable=False)

    # 是否是未分群组
    is_default = db.Column(db.Boolean, index=True, nullable=False)

    def to_json(self):
        res = model_to_dict(self, self.__class__)
        return res


class UserQunRelateInfo(db.Model):
    """
    每个人看到的群都是一个新群，所以整个项目的群id应该为这个表的自增项
    """
    __tablename__ = 'user_qun_relate_info'
    uqun_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, index=True, nullable=False)
    chatroomname = db.Column(db.String(32), index=True, nullable=False)

    # 该群属于哪个组
    group_id = db.Column(db.BigInteger, index=True, nullable=False)

    # 群中的机器人的昵称，如果为空则用用户默认机器人名称
    chatbot_nickname = db.Column(db.String(32), index=True, nullable=True)

    # 群先后顺序排名预留
    user_qun_seq = db.Column(db.Integer, index=True, nullable=False)
    create_time = db.Column(db.DateTime, index=True, nullable=False)

    # 当群被删除时，标记该群
    is_deleted = db.Column(db.Boolean, index=True, nullable=False)

    db.UniqueConstraint(user_id, chatroomname, name='ix_user_qun_relate_info_two_id')

    def to_json(self):
        res = model_to_dict(self, self.__class__)
        res.pop("chatroomname")
        return res


class UserQunBotRealteInfo(db.Model):
    """
    每个uqun中每个用户有哪些bot，这些bot的状态是否没有问题
    """
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_bot_rid = db.Column(db.BigInteger, index=True, nullable=False)
    is_error = db.Column(db.SmallInteger, index=True, nullable=False)


class CollaboratorUserRelateInfo(db.Model):
    """
    记录协作者对于每一个群的权限
    """
    rid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    collaborator_user_id = db.Column(db.BigInteger, index=True, nullable=False)
    admin_user_id = db.Column(db.BigInteger, index=True, nullable=False)

    # 标志这个人是否可以看到这个组中所有的设置
    view_send_qun_messages = db.Column(db.Boolean, index=True, nullable=False)
    view_qun_sign = db.Column(db.Boolean, index=True, nullable=False)
    view_auto_reply = db.Column(db.Boolean, index=True, nullable=False)
    view_welcome_message = db.Column(db.Boolean, index=True, nullable=False)

    # 标志这个人是否可以使用这些功能（使用这些功能不一定代表能看到之前的设置）
    func_send_qun_messages = db.Column(db.Boolean, index=True, nullable=False)
    func_qun_sign = db.Column(db.Boolean, index=True, nullable=False)
    func_auto_reply = db.Column(db.Boolean, index=True, nullable=False)
    func_welcome_message = db.Column(db.Boolean, index=True, nullable=False)
