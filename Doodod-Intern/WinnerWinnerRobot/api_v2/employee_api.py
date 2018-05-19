# -*- coding: utf-8 -*-
import time
import threading

from flask import request

from configs.config import main_api_v2
from core_v2.user_core import UserLogin
from models_v2.base_model import *
from utils.z_utils import *
from configs.config import GLOBAL_RULES_UPDATE_FLAG, GLOBAL_EMPLOYEE_PEOPLE_FLAG


@main_api_v2.route('/_employee_add_client', methods=["POST"])
@para_check('psw', 'username', 'client_id')
def _employee_add_client():
    if request.json.get('psw') != 'zvcasdkuagdgv214':
        return ' '
    try:
        new_client = CM('employee_client')
        new_client.username = request.json.get('username')
        new_client.client_id = request.json.get('client_id')
        new_client.remark = request.json.get('remark') if request.json.get('remark') is not None else 'sc'

        success = new_client.save()
        return response(new_client.to_json_full().update({'success': success, 'id': new_client.get_id()}))
    except Exception as e:
        return e


@main_api_v2.route('/_add_or_modify_tag', methods=["POST"])
@para_check('psw', 'index')
def add_or_modify_tag():
    if request.json.get('psw') != 'zvcasdkuagdgv214':
        return ' '
    value_as_dict = request.json
    value_as_dict.pop('psw')
    previous_tag = BaseModel.fetch_one('employee_tag', '*',
                                       BaseModel.where_dict({'index': int(request.json.get('index'))}))
    if previous_tag is None:
        new_tag = CM('employee_tag')
        new_tag.from_json(value_as_dict)
        flag = new_tag.save()
        return response({'success': flag, 'tag': new_tag.to_json_full()})
    else:
        previous_tag.from_json(value_as_dict)
        flag = previous_tag.save()
        return response({'success': flag, 'tag': previous_tag.to_json_full()})


@main_api_v2.route('/employee_search', methods=["POST"])
@para_check('keyword', )
def employee_search():
    try:
        keyword = unicode(request.json.get('keyword'))
        if keyword == "":
            return response({'err_code': -1, 'err_info': 'keyword could not be blank!'})
        user_list = BaseModel.fetch_all('a_contact', '*', BaseModel.or_(['=', 'alias', keyword],
                                                                        ['=', 'username', keyword],
                                                                        ['=', 'quan_pin', keyword],
                                                                        ['=', 'nickname', keyword], ),
                                        pagesize=100,
                                        page=1)
        result = []
        for i in user_list:
            _result = i.to_json_full()
            __username = _result.get('username')
            # pop chatroomname.
            if __username is not None and re.search(r'[0-9]+@chatroom', __username) is not None:
                continue
            result.append({'username': __username, 'nickname': _result.get('nickname'),
                           'avatar_url': _result.get('avatar_url')})
    except Exception as e:
        return response({'err_code': -1, 'err_info': '%s' % e})
    return response({'err_code': 0, 'content': result})


@main_api_v2.route('/employee_tags', methods=["POST"])
def employee_tags():
    res = {'err_code': 0, 'content': []}
    tag_list = BaseModel.fetch_all('employee_tag', '*', BaseModel.where_dict({'remark': 'sc'}))
    for i in tag_list:
        _tag = i.to_json_full()
        _tag.update({'_id': i.get_id()})
        res['content'].append({'id': _tag['index'], 'name': _tag['nickname'], '_id': _tag['_id']})
    return response(res)


@main_api_v2.route('/employee_tag_edit', methods=["POST"])
@para_check('token', 'username', 'tag_list')
def employee_tag_edit():
    # Check client or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        client_id = user_info.client_id
        client_username = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})
    if BaseModel.fetch_one('employee_client', '*', BaseModel.where_dict({'username': client_username})) is None:
        return response({'err_code': -2, 'content': 'User not our client.'})

    username = request.json.get('username')
    tag_list = request.json.get('tag_list')

    this_user = BaseModel.fetch_one('employee_people', '*', BaseModel.where_dict({'username': username}))

    if this_user is None:
        new_user = CM('employee_people')
        new_user.username = username
        new_user.tag_list = tag_list
        new_user.by_client_id = client_id
        new_user.remark = 'sc'
        flag = new_user.save()
    else:
        this_user.tag_list = tag_list
        this_user.by_client_id = client_id
        flag = this_user.save()
    # Update rule.
    GLOBAL_RULES_UPDATE_FLAG[GLOBAL_EMPLOYEE_PEOPLE_FLAG] = True
    if flag:
        return response({'err_code': 0, 'content': 'success'})
    else:
        return response({'err_code': -2, 'content': 'Failed'})


@main_api_v2.route('/employee_detail', methods=["POST"])
@para_check('username', )
def employee_detail():
    username = request.json.get('username')

    this_user = BaseModel.fetch_one('employee_people', '*', BaseModel.where_dict({'username': username}))

    if this_user is None:
        return response({'err_code': -1, 'err_info': 'Fake user.'})

    _tag_list = this_user.tag_list
    tag_list = []
    for i in _tag_list:
        this_tag_info = BaseModel.fetch_one('employee_tag', '*', BaseModel.where_dict({'index': i}))
        tag_list.append({'id': i, 'name': this_tag_info.nickname})

    user_info = BaseModel.fetch_one('a_contact', '*', BaseModel.where_dict({'username': username}))
    avatar_url = user_info.avatar_url
    nickname = user_info.nickname

    log_list = BaseModel.fetch_all('employee_be_at_log', '*', BaseModel.where_dict({'username': username}))
    be_at_count = 0
    overtime_count = 0
    avg_time = 0
    now = int(time.time())
    for i in log_list:
        be_at_count += 1
        if not i.is_reply and (int(i.create_time) + 86400) < now:
            overtime_count += 1
        if i.is_reply:
            avg_time += i.reply_time - i.create_time

    avg_time = avg_time / (be_at_count - overtime_count) if (be_at_count - overtime_count) else 0

    res = {'err_code': 0, 'content': {}}

    res['content']['user_info'] = {
        'avatar_url': avatar_url,
        'nickname': nickname,
        'username': username
    }

    res['content']['tag_list'] = tag_list

    res['content'].update({'be_at_count': be_at_count, 'overtime_count': overtime_count, 'avg_time': avg_time})

    return response(res)


@main_api_v2.route('/employee_record', methods=["POST"])
@para_check('username', 'page', 'pagesize')
def employee_record():
    try:
        username = request.json.get('username')
        page = int(request.json.get('page'))
        pagesize = int(request.json.get('pagesize'))

        log_list = BaseModel.fetch_all('employee_be_at_log', '*', BaseModel.where_dict({'username': username}),
                                       order_by=BaseModel.order_by({"create_time": "desc"}))

        all_log_list = log_list[(page - 1) * pagesize:page * pagesize]

        res = {"err_code": 0, 'content': {'total_count': len(log_list), 'log_list': []}}

        for log in all_log_list:
            chatroomname = log.chatroomname
            this_chatroom = BaseModel.fetch_one('a_chatroom', '*', BaseModel.where_dict({'chatroomname': chatroomname}))
            _temp = {
                'chatroom_info': {
                    'chatroom_name': chatroomname,
                    'nickname': this_chatroom.nickname if this_chatroom.nickname != '' else this_chatroom.nickname_default,
                    'avatar_url': this_chatroom.avatar_url,
                },
                'be_at_content': log.content,
                'create_time': log.create_time,
                'reply_duration': (log.reply_time - log.create_time) if log.is_reply and (
                        log.reply_time - log.create_time) < 86400 else -1
            }
            res['content']['log_list'].append(_temp)
    except Exception as e:
        return '%s' % e
    return response(res)


@main_api_v2.route('/employee_ranking', methods=['POST'])
def employee_ranking():
    try:
        people = BaseModel.fetch_all('employee_people', '*')
        res = {'err_code': 0, 'content': {'total_count': 0, 'user_info_list': []}}
        for this_user in people:
            username = this_user.username
            _tag_list = this_user.tag_list
            tag_list = []
            for i in _tag_list:
                this_tag_info = BaseModel.fetch_one('employee_tag', '*', BaseModel.where_dict({'index': i}))
                tag_list.append({'id': i, 'name': this_tag_info.nickname})

            user_info = BaseModel.fetch_one('a_contact', '*', BaseModel.where_dict({'username': username}))
            avatar_url = user_info.avatar_url
            nickname = user_info.nickname

            log_list = BaseModel.fetch_all('employee_be_at_log', '*', BaseModel.where_dict({'username': username}))
            be_at_count = 0
            overtime_count = 0
            avg_time = 0
            now = int(time.time())
            for i in log_list:
                be_at_count += 1
                if not i.is_reply and (int(i.create_time) + 86400) < now:
                    overtime_count += 1
                if i.is_reply:
                    avg_time += i.reply_time - i.create_time

            avg_time = avg_time / (be_at_count - overtime_count) if (be_at_count - overtime_count) else 0

            _temp = {
                "user_info": {
                    "username": username,
                    "avatar_url": avatar_url,
                    "nickname": nickname
                },
                "be_at_count": be_at_count,
                "overtime_count": overtime_count,
                "avg_time": avg_time,
                "tag_list": tag_list
            }
            res['content']['total_count'] += 1
            res['content']['user_info_list'].append(_temp)
    except Exception as e:
        return '%s' % e
    return response(res)
