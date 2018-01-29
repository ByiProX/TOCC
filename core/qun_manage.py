# -*- coding: utf-8 -*-


# 因为之前的表关系废掉了，所以现在需要重新写
# from config import db
# from models.qun_friend import GroupUserRelateInfo, GroupInfo, GroupQunRelateInfo
# from models.user_bot import UserInfo
#
#
# def set_default_group(user_info):
#     # 读取user_id
#     if isinstance(user_info, UserInfo):
#         pass
#     cur = db.session.query(GroupUserRelateInfo).filter(GroupUserRelateInfo.user_id == user_info.user_id).first()
#     if cur:
#         return 1
#     else:
#         _create_new_group(user_info.user_id, "未分组")
#
#         return 0
#
#
# def create_new_group(group_name, token=None, user_id=None):
#     if token and user_id:
#         raise ValueError("输入两个值")
#
#     if (not token) and (not user_id):
#         raise ValueError("没有输入用户信息")
#
#     if user_id:
#         _create_new_group(user_id, group_name)
#
#     if token:
#         user_info = db.session.query(UserInfo.token == UserInfo.token).first()
#         user_id = user_info.user_id
#         _create_new_group(user_id, group_name)
#
#
# def rename_a_group(group_rename, group_id):
#     group_info = db.session.query(GroupInfo.group_id == group_id).first()
#     group_info.group_name = group_rename
#     db.session.commit()
#
# def transfor_qun_into_a_group(group_qun_id,new_group_id):
#
#     gqr_info = db.session.query(GroupQunRelateInfo.group_qun_id == group_qun_id).first()
#     gqr_info.group_id = new_group_id
#     db.session.commit()
#
# def delete_a_group(group_id):
#     group_info = db.session.query(GroupInfo.group_id == group_id).first()
#     gur_info = db.session.query(GroupUserRelateInfo.group_id == group_id).all()
#
#     for each_gur_info in gur_info:
#
#
#         if each_gur_info.is_default_group is True:
#
#             return 1
#
#
#         # raise NotImplementedError
#
#
#
#         db.session.delete(each_gur_info)
#
#     gqr_info = db.session.query(GroupQunRelateInfo.group_id == group_id).all()
#     for each_gqr_info in gqr_info:
#         each_gqr_info.group_id =
#
#
#
#
# def _create_new_group(user_id, group_name):
#     group_info = GroupInfo()
#     group_info.group_name = group_name
#     db.session.add(group_info)
#     db.session.commit()
#
#     gur_info = GroupUserRelateInfo()
#     gur_info.group_id = group_info.group_id
#     gur_info.user_id = user_id
#     gur_info.is_default_group = True
#     gur_info.is_admin = True
#     gur_info.is_viewer = True
#     gur_info.view_send_qun_messages = True
#     gur_info.view_qun_sign = True
#     gur_info.view_auto_reply = True
#     gur_info.view_welcome_message = True
#     gur_info.func_send_qun_messages = False
#     gur_info.func_qun_sign = False
#     gur_info.func_auto_reply = False
#     gur_info.func_welcome_message = False
#     db.session.add(gur_info)
#     db.session.commit()
