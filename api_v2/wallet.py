# -*- coding: utf-8 -*-

import logging

from flask import request, jsonify

from configs.config import ERR_PARAM_SET, main_api_v2
from core_v2.user_core import UserLogin
from utils.u_response import make_response

from models_v2.base_model import *
from functools import wraps

logger = logging.getLogger('main')


def para_check(need_list, *parameters):
    def _wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _para_check = parameters_check(need_list, *parameters)
            if _para_check is not True:
                return _para_check
            return func(*args, **kwargs)

        return wrapper

    return _wrapper


def parameters_check(need_list, *args):
    """Check each parameter (For POST)
    if could not get this parameter return 'Lack of (parameter)'
    """

    if request.json is None:
        return response({'err_code': -1, 'content': 'Lack of json.'})

    if isinstance(need_list, str):
        need = args + (need_list,)
    else:
        need = need_list + args

    for i in need:
        if request.json.get(i) is None:
            return response({'err_code': -1, 'content': 'Lack of %s.' % i})
    return True


def response(body_as_dict):
    """Use make_response or not."""
    response_body = jsonify(body_as_dict)
    return response_body


@main_api_v2.route('/wallets', methods=['POST'])
def app_wallets():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    page = request.json.get('page')
    pagesize = request.json.get('pagesize')
    if not page:
        page = 1
    if not page:
        pagesize = 10

    chatroomname = request.json.get('chatroomname')

    where = BaseModel.where_dict({"client_id": user_info.client_id})
    if chatroomname:
        where = BaseModel.where_dict({"client_id": user_info.client_id, "chatroomname": chatroomname})

    wallet_list = BaseModel.fetch_all('wallet', '*', where, page=1, pagesize=pagesize)

    client_switch = BaseModel.fetch_one('client_switch', '*', BaseModel.where_dict({"client_id": user_info.client_id}))

    switch = 0
    if client_switch:
        switchJson = client_switch.to_json()
        switch = switchJson['func_coin_wallet']

    data = []
    wxIds = []
    for w in wallet_list:
        _w = w.to_json()
        wxIds.append(_w['username'])

        # wxUserInfo = BaseModel.fetch_one('a_contact', 'nickname,avatar_url' ,BaseModel.where_dict({"username":_w['username']}))
        # if(wxUserInfo):
        #    _wxUserInfo = wxUserInfo.to_json()
        #    _w.update({"uinfo":[_wxUserInfo['nickname'],_wxUserInfo['avatar_url']]})
        data.append(_w)

    if len(wxIds) >= 1:
        wxUserInfo = BaseModel.fetch_all('a_contact', ['nickname', 'username', 'avatar_url'],
                                         BaseModel.where("in", "username", wxIds))
        if wxUserInfo:
            for wu in wxUserInfo:
                uinfo = wu.to_json()
                for da in data:
                    if da['username'] == uinfo['username']:
                        da.update({"uinfo": {"nickname": uinfo['nickname'], "avatar_url": uinfo['avatar_url']}})

    return make_response(SUCCESS, wallet_list=data, switch=switch)


@main_api_v2.route('/wallets_switch', methods=['POST'])
def app_wallets_switch():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switch = request.json.get('switch')
    if switch is None:
        return make_response(ERR_PARAM_SET)

    switchModel = BaseModel.fetch_one('client_switch', '*', BaseModel.where_dict({"client_id": user_info.client_id}))
    switchModel.func_coin_wallet = switch

    if switchModel.save() is True:
        return make_response(SUCCESS, switch=switch)
    else:
        return make_response(ERR_PARAM_SET)


@main_api_v2.route('/get_wallet_status', methods=['POST'])
@para_check('token')
def get_wallet_status():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switchModel = BaseModel.fetch_one('client_switch', '*', BaseModel.where_dict({"client_id": user_info.client_id}))

    if switchModel.func_coin_wallet:
        result = True
    else:
        result = False

    return response({'err_code': 0, 'content': {'status': result}})


@main_api_v2.route('/get_chatroom_list', methods=['POST'])
@para_check('token', 'keyword')
def get_chatroom_list():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)
    client_id = user_info.client_id
    keyword = request.json.get('keyword')
    _temp = BaseModel.fetch_all('wallet', '*', BaseModel.where_dict({'client_id': client_id}))


    result = {
        'err_code': 0,
        'content': {
            'chatroom_list': []
        }
    }

    _chatroom_name_list = []

    for i in _temp:
        if keyword in i.user_nick or keyword in i.address :
            if i.chatroomname not in _chatroom_name_list:
                _chatroom_name_list.append(i.chatroomname)
                result['content']['chatroom_list'].append({'chatroom_nickname': i.chatroom_nick, 'chatroomname': i.chatroomname})


    return response(result)
