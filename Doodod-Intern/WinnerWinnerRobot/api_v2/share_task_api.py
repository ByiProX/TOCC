# -*- coding: utf-8 -*-

from flask import request
from configs.config import *
from core_v2.user_core import UserLogin
from models_v2.base_model import BaseModel, CM
from utils.u_model_json_str import verify_json
from utils.u_response import make_response


@main_api_v2.route("/create_share_task", methods = ['POST'])
def create_task():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    ori_url = request.json.get("ori_url")
    title = request.json.get("title")
    if not ori_url or not title:
        return make_response(ERR_INVALID_PARAMS)
    thumb_url = request.json.get("thumb_url")
    desc = request.json.get("desc")

    share_task = CM(ShareTask).generate_create_time().generate_update_time()
    share_task.is_deleted = 0
    share_task.ori_url = ori_url
    share_task.title = title
    share_task.thumb_url = thumb_url
    share_task.desc = desc
    share_task.client_id = user_info.client_id

    share_task.save()

    share_state = generate_share_state(share_task)

    return make_response(SUCCESS, share_task = share_task.to_json_full())


@main_api_v2.route("/get_share_list", methods = ['POST'])
def api_get_share_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    page = request.json.get("page", DEFAULT_PAGE)
    pagesize = request.json.get("pagesize", DEFAULT_PAGE_SIZE)

    share_list = BaseModel.fetch_all(ShareTask, "*", where_clause = BaseModel.where_dict({"client_id", user_info.client_id}), page = page, pagesize = pagesize, order_by = BaseModel.order_by({"create_time": "desc"}))
    share_list_json = [r.to_json_full for r in share_list]

    return make_response(SUCCESS, share_list = share_list_json)


@main_api_v2.route("/share_task", methods = ['POST'])
def api_share_task():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    return make_response(SUCCESS)


@main_api_v2.route("/get_state_by_state", methods = ['POST'])
def api_get_state_by_state():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    return make_response(SUCCESS)


def generate_share_state(share_task):
    share_state = ""
    return share_state


def extract_share_state():
    # share_state = ""
    # return share_state
    pass

