# -*- coding: utf-8 -*-
__author__ = "Quentin"

from flask import request, send_file
from configs.config import main_api_v2, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from utils.u_response import make_response
from models_v2.base_model import *
import time
import xlwt
import os

logger = logging.getLogger('main')


@main_api_v2.route('/get_wallets_excel', methods=['GET'])
def get_wallets_excel():
    status, user_info = UserLogin.verify_token(request.args.get('token'))
    chatroom = request.args.get('chatroomname', 0)
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    workbook = xlwt.Workbook(encoding="utf-8")

    wallets = BaseModel.fetch_all("wallet", "*",
                                  where_clause=BaseModel.where_dict(
                                      {"client_id": client_id}
                                  ))

    if not wallets:
        return make_response(ERR_WRONG_ITEM)

    if not chatroom:
        chatroomname_list = set([wallet.chatroomname for wallet in wallets])
    else:
        chatroomname_list = [chatroom]

    for chatroomname in chatroomname_list:
        chatroom_info = BaseModel.fetch_one("a_chatroom", "*",
                                            where_clause=BaseModel.where_dict(
                                                {"chatroomname": chatroomname}))

        worksheet = workbook.add_sheet(chatroom_info.nickname_real)

        worksheet.write(0, 0, label="用户名")
        worksheet.write(0, 1, label="来自群")
        worksheet.write(0, 2, label="钱包地址")
        worksheet.write(0, 3, label="获取时间")

        i = 1
        for wallet in wallets:
            if chatroomname == wallet.chatroomname:
                user = BaseModel.fetch_one("a_contact", "*",
                                           where_clause=BaseModel.where_dict(
                                               {"username": wallet.username}
                                           ))
                worksheet.write(i, 0, user.nickname)
                worksheet.write(i, 1, chatroom_info.nickname_real)
                worksheet.write(i, 2, wallet.address)
                worksheet.write(i, 3, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(wallet.create_time)))
                i += 1

    file_name = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' wallets.xls'
    file_path = os.path.join(os.getcwd(), "static", file_name)
    workbook.save(file_path)

    resp = send_file(file_path)
    resp.headers["Content-Disposition"] = "attachment; filename=%s" % file_name
    return resp


@main_api_v2.route('/get_sensitive_excel', methods=['GET'])
def get_sensitive_excel():
    status, user_info = UserLogin.verify_token(request.args.get('token'))
    if status != SUCCESS:
        return make_response(status)

    owner = user_info.client_id
    workbook = xlwt.Workbook(encoding="utf-8")

    monitor_feedbacks = BaseModel.fetch_all("sensitive_message_log", "*",
                                            where_clause=BaseModel.where_dict(
                                                {"owner": owner}),
                                            order_by=BaseModel.order_by({"create_time": "desc"})
                                            )

    if not monitor_feedbacks:
        return make_response(ERR_WRONG_ITEM)

    sheet_dict = {
        0: "监控内容",
        1: "聊天内容",
        2: "所属微信群",
        3: "发言人",
        4: "发言时间"
    }
    worksheet = workbook.add_sheet("消息监控统计")
    for key, value in sheet_dict.items():
        worksheet.write(0, key, label=value)

    for i, monitor_feedback in enumerate(monitor_feedbacks, start=1):
        worksheet.write(i, 0, monitor_feedback.sensitive_word)

        worksheet.write(i, 1, monitor_feedback.content)

        chatroom_info = BaseModel.fetch_one("a_chatroom", "*",
                                            where_clause=BaseModel.where_dict(
                                                {"chatroomname": monitor_feedback.chatroomname}))
        worksheet.write(i, 2, chatroom_info.nickname_real)

        user_info = BaseModel.fetch_one("a_contact", "*",
                                        where_clause=BaseModel.where_dict(
                                            {"username": monitor_feedback.speaker_username}
                                        ))
        worksheet.write(i, 3, user_info.nickname)

        worksheet.write(i, 4, time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(monitor_feedback.create_time)))

    file_name = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' sensitive.xls'
    file_path = os.path.join(os.getcwd(), "static", file_name)
    workbook.save(file_path)

    resp = send_file(file_path)
    resp.headers["Content-Disposition"] = "attachment; filename=%s" % file_name
    return resp
