# -*- coding: utf-8 -*-
__author__ = "Quentin"

from flask import request
from models_v2.base_model import BaseModel, CM
from configs.config import SUCCESS, ERR_WRONG_ITEM, main_api_v2
from core_v2.user_core import UserLogin
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from pprint import pprint


@main_api_v2.route('/get_paid_quns', methods=['POST'])
def app_get_paid_quns():
    """
    获取当前的可用的群
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    try:
        client_qun_statistic = BaseModel.fetch_one("client",
                                                   ["client_name", "qun_count", "qun_used"],
                                                   where_clause=BaseModel.and_(
                                                       ["=", "client_id", user_info.client_id]
                                                   )).to_json()
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    try:
        quns_paid = BaseModel.fetch_all("client_qun_r", "*",
                                        where_clause=BaseModel.and_(
                                            ["=", "client_id", user_info.client_id],
                                            ["=", "is_paid", 1],
                                            ["=", "status", 1]
                                        ))
        quns_paid = [qun_paid.to_json() for qun_paid in quns_paid]
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS, client_qun_statis=client_qun_statistic, quns_paid=quns_paid)


@main_api_v2.route('/add_paid_quns', methods=['POST'])
def app_add_paid_quns():
    """
    增加可用的群数量qun_count
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))

    if status != SUCCESS:
        return make_response(status)

    add_qun_num = request.json.get("add_qun_num", 0)

    try:
        client = BaseModel.fetch_one("client", "*",
                                     where_clause=BaseModel.and_(
                                         ["=", "client_id", user_info.client_id],
                                     ))

        client.qun_count += add_qun_num
        client.save()
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS)


# 以下不对外开放
@main_api_v2.route('/add_used_quns', methods=['POST'])
def __app_add_paid_quns():
    """
    控制已使用的群的数量qun_used
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))

    if status != SUCCESS:
        return make_response(status)

    add_qun_used_num = request.json.get("add_qun_used_num", 0)

    try:
        client = BaseModel.fetch_one("client", "*",
                                     where_clause=BaseModel.and_(
                                         ["=", "client_id", user_info.client_id],
                                     ))

        client.qun_used += add_qun_used_num
        client.save()
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS)


@main_api_v2.route('/get_wkx_quns', methods=['POST'])
def __app_get_wkx_quns():
    """
    查看自己的微信群数量状态
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))

    if status != SUCCESS:
        return make_response(status)

    try:
        client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                          where_clause=BaseModel.and_(
                                              ["=", "client_id", user_info.client_id],
                                              ["=", "status", 1]
                                          ),
                                          order_by=BaseModel.order_by({"create_time": "desc"})
                                          )

        wkx_quns = [client_qun.to_json_full() for client_qun in client_quns]
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS, wkx_quns=wkx_quns)


@main_api_v2.route('/change_qun_is_paid_status', methods=['POST'])
def __app_change_qun_is_paid_status():
    """
    查看自己的微信群数量状态
    """
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))

    if status != SUCCESS:
        return make_response(status)

    chatroomname = request.json.get("chatroomname")
    is_paid = request.json.get("is_paid")

    try:
        client_qun = BaseModel.fetch_one("client_qun_r", "*",
                                         where_clause=BaseModel.and_(
                                             ["=", "client_id", user_info.client_id],
                                             ["=", "chatroomname", chatroomname],
                                             ["=", "status", 1]
                                         ))
        client_qun.is_paid = is_paid
        client_qun.save()

    except Exception:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS)


if __name__ == "__main__":
    free_clients = BaseModel.fetch_all("client", "*",
                                       where_clause=BaseModel.and_(
                                           [">=", "qun_count", "qun_used"],
                                       ))
    # print free_clients

    client_quns = BaseModel.fetch_all("client_qun_r", "*",
                                      where_clause=BaseModel.and_(
                                          ["=", "client_id", 5],
                                      ))

    print client_quns.__len__()
