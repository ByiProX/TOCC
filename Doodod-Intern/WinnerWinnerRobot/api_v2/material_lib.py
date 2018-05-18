# -*- coding: utf-8 -*-
__author__ = "Quentin"

from flask import request
from configs.config import main_api_v2, SUCCESS, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from models_v2.base_model import BaseModel
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
import logging

logger = logging.getLogger('main')


@main_api_v2.route("/get_material_lib_list", methods=['POST'])
def get_material_lib_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    real_type = request.json.get('real_type', 0)
    page = request.json.get('page')
    pagesize = request.json.get('pagesize')
    order_type = request.json.get('order_type', 'desc')

    if not real_type:
        real_type_list = [i for i in range(2, 8)]
    else:
        real_type_list = [real_type]

    try:
        materials = BaseModel.fetch_all("material_lib", "*",
                                        where_clause=BaseModel.and_(
                                            ["=", "client_id", client_id],
                                            ["=", "is_deleted", 0],
                                            ["in", "real_type", real_type_list]
                                        ),
                                        page=page, pagesize=pagesize,
                                        order_by=BaseModel.order_by({"create_time": order_type})
                                        )
        materials = [material.to_json_full() for material in materials]
    except Exception as e:
        # logger.error(e.message)
        return make_response(ERR_WRONG_ITEM)

    try:
        for material in materials:
            message_info = BaseModel.fetch_all('a_message',
                                               ["source_url", "img_path",
                                                "thumb_url", "title",
                                                "desc", "size",
                                                "duration", "real_content", "msg_local_id", "msg_svr_id", "talker"],
                                               where_clause=BaseModel.where_dict(
                                                   {"msg_id": material.get("msg_id")}
                                               ))[0]
            material.update(message_info.to_json())

        return make_response(SUCCESS, materials=materials)
    except Exception as e:
        return make_response(ERR_WRONG_ITEM)


@main_api_v2.route("/delete_material_lib_list", methods=['POST'])
def delete_material_lib_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    msg_id = request.json.get('msg_id')
    if not msg_id:
        logger.error(u"无法找到该message id: %s." % msg_id)
        return make_response(ERR_WRONG_ITEM)
    try:
        material = BaseModel.fetch_all('material_lib', '*',
                                       where_clause=BaseModel.where_dict(
                                           {"msg_id": msg_id}))[0]
        material.is_deleted = 1
        material.update()
        return make_response(SUCCESS)
    except Exception as e:
        return make_response(ERR_WRONG_ITEM)


if __name__ == "__main__":
    BaseModel.extract_from_json()
    s = BaseModel.fetch_one("a_contact", '*', where_clause=BaseModel.where_dict({'username': 'wxid_wn6vt38xa97c22'}))

    s.province = "beijingbeijingbeijing"
    s.delete()

    # print s.to_json_full().__len__()
    # print s.to_json().__len__()

    ms = BaseModel.fetch_all("material_lib", "*",
                             where_clause=BaseModel.and_(
                                 ["=", "client_id", 1],
                                 ["=", "is_deleted", 0],
                             ),
                             page=1, pagesize=20)

    print ms.__len__()
    # UserLogin.verify_token(request.json.get('token'))
    # print status
    # material = BaseModel.fetch_all('a_message', '*',
    #                                where_clause=BaseModel.where_dict(
    #                                    {"msg_id": "d3hpZF9sNjZtNnd1aWx1ZzkxMl8xODlfMTUyNTg2ODUyNw=="}))

    # print material
