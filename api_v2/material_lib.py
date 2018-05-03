# -*- coding: utf-8 -*-
__author__ = "Quentin"

from flask import request
from configs.config import main_api_v2, SUCCESS, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from models_v2.base_model import BaseModel
from utils.u_model_json_str import verify_json
from utils.u_response import make_response


@main_api_v2.route("/material_lib_list", methods=['POST'])
def read_material_lib_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    page = request.json.get('page')
    pagesize = request.json.get('pagesize')
    order_type = request.json.get('order_type', 'desc')

    try:
        materials = BaseModel.fetch_all("material_lib", "*",
                                        where_clause=BaseModel.where_dict(
                                            {"client_id": client_id}),
                                        page=page, pagesize=pagesize,
                                        order_by=BaseModel.order_by({"create_time": order_type}
                                                                    ))
        materials = [material.to_json_full() for material in materials]
    except:
        return make_response(ERR_WRONG_ITEM)

    try:
        for material in materials:
            message_info = BaseModel.fetch_all('a_message', '*',
                                               where_clause=BaseModel.where_dict(
                                                   {"msg_local_id": material.get("msg_id")}
                                               ))[0]
            material["messages_info"] = message_info.to_json_full()
            return make_response(SUCCESS, materials=materials)

    except:
        return make_response(ERR_WRONG_ITEM)
