# -*- coding: utf-8 -*-

from config import db


# 整体结构需要重做，一方面一个群只能在一个组里面，另一方面，所有的属性和权限要精确到群而不是精确到组
# class GroupInfo(db.Model):
#     """
#     存储用户的分组
#     """
#     __tablename__ = "group_info"
#     group_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#
#     # 组名称，如果不设置则有默认，不能为空
#     group_name = db.Column(db.String(16), index=True, nullable=False)
#
#
# class GroupUserRelateInfo(db.Model):
#     """
#     存储每个组与每个用户的关系，同时代表着每个用户对每个组的总权限，各个功能控制权限等等
#     """
#     __tablename__ = "group_user_relate_info"
#     group_user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#     group_id = db.Column(db.BigInteger, index=True, nullable=False)
#     user_id = db.Column(db.BigInteger, index=True, nullable=False)
#     is_default_group = db.Column(db.Boolean, index=True, nullable=False)
#
#     # 用于标志这个组谁是最大权限（初始情况下代表这个群是谁建立的）
#     is_admin = db.Column(db.Boolean, index=True, nullable=False)
#
#     # 用于标志这个组中这个人是否有看的权限（有看这个组的权限不一定有看这个组的其他权限，只是说能看到这个组）
#     is_viewer = db.Column(db.Boolean, index=True, nullable=False)
#
#     # 标志这个人是否可以看到这个组中所有的设置
#     view_send_qun_messages = db.Column(db.Boolean, index=True, nullable=False)
#     view_qun_sign = db.Column(db.Boolean, index=True, nullable=False)
#     view_auto_reply = db.Column(db.Boolean, index=True, nullable=False)
#     view_welcome_message = db.Column(db.Boolean, index=True, nullable=False)
#
#     # 标志这个人是否可以使用这些功能（使用这些功能不一定代表能看到之前的设置）
#     func_send_qun_messages = db.Column(db.Boolean, index=True, nullable=False)
#     func_qun_sign = db.Column(db.Boolean, index=True, nullable=False)
#     func_auto_reply = db.Column(db.Boolean, index=True, nullable=False)
#     func_welcome_message = db.Column(db.Boolean, index=True, nullable=False)
#
#     db.UniqueConstraint(group_id, user_id, name='ix_group_user_relate_info_two_id')
#
#
# class GroupQunRelateInfo(db.Model):
#     """
#     存储每个组中有哪些群
#     目前改为了一个群只能被分配到一个分组中
#     """
#     __tablename__ = "group_qun_relate_info"
#     group_qun_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#     group_id = db.Column(db.BigInteger, index=True, nullable=False)
#     chatroomname = db.Column(db.String(32), index=True, unique=True, nullable=False)
#     is_deleted = db.Column(db.Boolean, index=True, nullable=False)
#
#     # db.UniqueConstraint(group_id, chatroomname, name='ix_group_qun_relate_info_two_id')
