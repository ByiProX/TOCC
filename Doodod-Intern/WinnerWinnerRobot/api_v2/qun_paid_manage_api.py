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
                                            ["=", "is_paid", 1]
                                        ))
        quns_paid = [qun_paid.to_json() for qun_paid in quns_paid]
    except Exception:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS, client_qun_statis=client_qun_statistic, quns_paid=quns_paid)


@main_api_v2.route('/add_paid_quns', methods=['POST'])
def app_add_paid_quns():
    """
    增加群数量
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


if __name__ == "__main__":
    free_clients = BaseModel.fetch_all("client", "*",
                                       where_clause=BaseModel.and_(
                                           [">=", "qun_count", "qun_used"],
                                       ))
    print free_clients
