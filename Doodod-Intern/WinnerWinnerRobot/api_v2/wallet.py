# -*- coding: utf-8 -*-

import logging

from flask import request, jsonify, send_file

from configs.config import ERR_PARAM_SET, main_api_v2, SUCCESS, ERR_WRONG_ITEM
from core_v2.user_core import UserLogin
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from utils.z_utils import para_check,response
from utils.tag_handle import Tag
from models_v2.base_model import *


logger = logging.getLogger('main')



@main_api_v2.route('/wallets', methods=['POST'])
def app_wallets():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    page = request.json.get('page')
    pagesize = request.json.get('pagesize')
    limit = request.json.get('limit')
    offset = request.json.get('offset')
    if not page:
        page = 1
    if not page:
        pagesize = 10

    chatroomname = request.json.get('chatroomname')

    where = BaseModel.where_dict({"client_id": user_info.client_id})
    if chatroomname:
        where = BaseModel.where_dict({"client_id": user_info.client_id, "chatroomname": chatroomname})

    total_count = BaseModel.count('wallet', where)
    wallet_list = BaseModel.fetch_all('wallet', '*', where, page=1, pagesize=pagesize, offset=BaseModel.offset(offset),
                                      limit=BaseModel.limit(limit))

    client_switch = BaseModel.fetch_one('client_switch', '*', BaseModel.where_dict({"client_id": user_info.client_id}))

    switch = 0
    if client_switch:
        switchJson = client_switch.to_json()
        switch = switchJson['func_coin_wallet']

    data = []
    wxIds = []
    for w in wallet_list:
        _w = w.to_json_full()
        _w['id'] = w.get_id()
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

    return make_response(SUCCESS, wallet_list=data, switch=switch, total_count=total_count)


@main_api_v2.route('/wallets_switch', methods=['POST'])
@para_check('token', 'switch')
def app_wallets_switch():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # Switch func.
    switch = request.json.get('switch')
    if switch not in (True, False):
        return response({'err_code': -1})
    if switch:
        user_info.func_switch = Tag(user_info.func_switch).put_name('wallet').as_int()
    else:
        user_info.func_switch = Tag(user_info.func_switch).delete_name('wallet').as_int()
    user_info.save()

    switchModel = BaseModel.fetch_one('client_switch', '*', BaseModel.where_dict({"client_id": user_info.client_id}))
    switchModel.func_coin_wallet = switch

    if switchModel.save() is True:
        return make_response(SUCCESS, switch=switch)
    else:
        return make_response(ERR_PARAM_SET)


@main_api_v2.route('/get_wallet_status', methods=['POST'])
@para_check('token')
def get_wallet_status():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    switchModel = BaseModel.fetch_one('client_switch', '*', BaseModel.where_dict({"client_id": user_info.client_id}))

    if switchModel and switchModel.func_coin_wallet:
        result = True
    else:
        result = False

    return response({'err_code': 0, 'content': {'func_coin_wallet': result}})


@main_api_v2.route('/get_wallet_chatroom_list', methods=['POST'])
@para_check('token', 'keyword')
def get_chatroom_list():
    verify_json()
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
        _user_nick = i.user_nick
        _address = i.address
        if _user_nick is None:
            _user_nick = ''
        if _address is None:
            _address = ''

        # by qurntin 将chatroom_nick 修改为 chatroom_nickname
        if keyword in _user_nick or keyword in _address:
            if i.chatroomname not in _chatroom_name_list:
                _chatroom_name_list.append(i.chatroomname)
                result['content']['chatroom_list'].append(
                    {'chatroom_nickname': i.chatroom_nickname, 'chatroomname': i.chatroomname})

    return response(result)


@main_api_v2.route('/wallets_delete', methods=['POST'])
@para_check('id', 'token')
def app_wallets_delete():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    _id = request.json.get('id')
    if _id is None:
        return make_response(ERR_PARAM_SET)

    ret = CM("wallet").set_id(_id).db_delete()

    if ret is True:
        return make_response(SUCCESS, id=_id)
    else:
        return make_response(ERR_PARAM_SET)

