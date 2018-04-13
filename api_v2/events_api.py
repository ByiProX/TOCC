# -*- coding: utf-8 -*-
import os
import time
import logging

import requests
from flask import request, jsonify
from functools import wraps

from configs.config import main_api_v2 as app_test
from core_v2.user_core import UserLogin
from models_v2.base_model import *

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


@app_test.route('/events_init', methods=['POST'])
@para_check('token')
def create_event_init():
    """Create a base event."""
    # Check owner or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'Wrong user.'})
    # Check if previous event is not finished.
    # event_instance = Event.query.filter(Event.owner == owner).all()
    event_instance = BaseModel.fetch_all('events', '*', BaseModel.where_dict({"owner": owner}))
    if event_instance:
        for i in event_instance:
            if i.is_finish == 0:
                # previous_event = db.session.query(Event).filter(Event.owner == owner,
                #                                                 Event.is_finish == False).first()
                previous_event = BaseModel.fetch_one('events', '*',
                                                     BaseModel.where_dict({"owner": owner, "is_finish": 0}))
                alive_qrcode_url = 'http://imtagger.com/www/#/pull-group-qr/%s' % previous_event.events_id
                event_id = previous_event.events_id
                return response({'err_code': 0, 'content': {'alive_qrcode_url': alive_qrcode_url,
                                                            'fission_word_1': '嗨！恭喜您即将获取「3点钟无眠区块链」听课资格！ 1.转发以上图片+文字到朋友圈或者100以上群聊中 2.不要屏蔽好友，转发后截图发至本群 3.转发后在本群等待听课即可 分享图片及内容如下 ↓↓↓↓↓ ',
                                                            'fission_word_2': '区块链行业大咖邀请您在4月28日收听课程【3点钟无眠区块链】 名额有限 快扫码入群吧！ ',
                                                            'condition_word': '3点种无眠区块链共同学习赚钱群，现在限时免费获取听课资格，满员开课哦！ ',
                                                            'pull_people_word': '3点种无眠区块链共同学习赚钱群，现在限时免费获取听课资格，满员开课哦！ ',
                                                            'event_id': event_id}})
    # Create base event.
    # new_event = Event(owner=owner)
    # db.session.add(new_event)
    # db.session.commit()
    new_event = CM('events')
    new_event.owner = owner
    new_event.is_finish = 0
    new_event.save()
    # Add QRcode URL.
    # previous_event = db.session.query(Event).filter(Event.owner == owner, Event.is_finish == False).first()
    previous_event = BaseModel.fetch_one('events', '*',
                                         BaseModel.where_dict({"owner": owner, "is_finish": 0}))
    alive_qrcode_url = 'http://imtagger.com/www/#/pull-group-qr/%s' % previous_event.events_id
    previous_event.alive_qrcode_url = alive_qrcode_url
    # db.session.commit()
    previous_event.update()
    # Static word.
    result = {
        'fission_word_1': '嗨！恭喜您即将获取「3点钟无眠区块链」听课资格！ 1.转发以上图片+文字到朋友圈或者100以上群聊中 2.不要屏蔽好友，转发后截图发至本群 3.转发后在本群等待听课即可 分享图片及内容如下 ↓↓↓↓↓ ',
        'fission_word_2': '区块链行业大咖邀请您在4月28日收听课程【3点钟无眠区块链】 名额有限 快扫码入群吧！ ',
        'condition_word': '3点种无眠区块链共同学习赚钱群，现在限时免费获取听课资格，满员开课哦！ ',
        'pull_people_word': '3点种无眠区块链共同学习赚钱群，现在限时免费获取听课资格，满员开课哦！ ',
        'alive_qrcode_url': alive_qrcode_url,
    }

    return response({'err_code': 0, 'content': result})


@app_test.route('/events_create', methods=['POST'])
@para_check('token')
def create_event():
    """Create a full event."""
    # Check owner or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})
    # Check previous init.
    # temp_check = db.session.query(Event).filter(Event.owner == owner, Event.is_finish == False).first()
    temp_check = BaseModel.fetch_one('events', '*',
                                     BaseModel.where_dict({"owner": owner, "is_finish": 0}))
    if not temp_check:
        return response({'err_code': -2, 'content': 'Previous init does not exist.'})
    # Check parameters and save.
    full_event_paras = (
        'event_title', 'start_time', 'end_time', 'start_index', 'start_name',
        'chatroom_name_protect',
        'chatroom_repeat_protect', 'need_fission', 'need_condition_word', 'need_pull_people', 'fission_word_1',
        'fission_word_2', 'condition_word', 'pull_people_word')
    full_event_paras_as_dict = {}
    for i in full_event_paras:
        if request.json.get(i) is None:
            return response({'err_code': -1, 'content': 'Lack of %s' % i})
        else:
            full_event_paras_as_dict[i] = request.json.get(i)
    # [Fix]
    static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static')
    try:
        os.mkdir(static_path)
    except Exception:
        pass
    new_file = new_file_path(static_path)
    if request.json.get('poster_raw'):
        with open(new_file, 'wb') as f:
            f.write(request.json.get('poster_raw'))
        full_event_paras_as_dict['poster_raw'] = new_file
    else:
        full_event_paras_as_dict['poster_raw'] = ' '
    # Create a full event.
    # [Improve] string to bytes.
    full_event_paras_as_dict['is_finish'] = 1
    # True -> 1, False ->0
    _temp = full_event_paras_as_dict.copy()
    for k, v in _temp.items():
        if v is True:
            full_event_paras_as_dict[k] = 1
        if v is False:
            full_event_paras_as_dict[k] = 0
    # event_id = db.session.query(Event).filter(Event.owner == owner, Event.is_finish == False).first().id
    # db.session.query(Event).filter(Event.owner == owner, Event.is_finish == False).update(full_event_paras_as_dict)
    # db.session.commit()
    event = BaseModel.fetch_one('events', '*',
                                BaseModel.where_dict({"owner": owner, "is_finish": 0}))
    event_id = event.events_id
    # Fix is_work
    full_event_paras_as_dict.update({'is_work': 1})
    event.from_json(full_event_paras_as_dict)

    # Create a chatroom for this event. index = start_index.
    chatroom_nickname = to_str(event.start_name) + str(event.start_index) + '群'
    bot_username = BaseModel.fetch_one('client_bot_r', '*', BaseModel.where_dict({'client_id': event.owner})).bot_username
    create_chatroom_dict = {
        'bot_username':bot_username,
        'data':{
            'task': 'create_chatroom',
            "owner": event.owner,
            "chatroom_nickname": chatroom_nickname
        }
    }
    try:
        create_chatroom_resp = requests.post('http://47.75.83.5/android/send_message', json=create_chatroom_dict)
    except Exception as e:
        logger.warning('Create chatroom request error:{}'.format(e))
    # Add chatroom info in relationship.
    events_chatroom = CM('events_chatroom')
    events_chatroom.index = event.start_index
    events_chatroom.chatroomname = 'Tobe'
    events_chatroom.event_id = event.events_id

    # Save at final.
    events_chatroom.save()
    event.save()
    return response({'err_code': 0, 'content': {'event_id': event_id}})


@app_test.route('/events_delete', methods=['POST'])
@para_check('token', 'event_id')
def disable_events():
    # Check token and event_id.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    owner = user_info.username
    event_id = int(request.json.get('event_id'))
    # Search event.
    # temp_check = db.session.query(Event).filter(Event.owner == owner, Event.id == event_id).first()
    temp_check = BaseModel.fetch_by_id('events', event_id)
    if temp_check is None:
        return response({'err_code': -2, 'content': 'Logical error.'})
    else:
        temp_check.is_work = 0
        # db.session.commit()
        temp_check.save()
        return response({'err_code': 0, 'content': 'SUCCESS'})


@app_test.route('/events_qrcode', methods=['POST'])
@para_check('token', 'event_id')
def get_events_qrcode():
    """Get event base info (for qrcode)."""
    event_id = request.json.get('event_id')
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})
    # Handle.
    event = BaseModel.fetch_by_id('events', event_id)
    # Use event_id search chatroom list, then get a prepared chatroom
    # and return its chatroomname.
    event_start = event.start_time
    event_end = event.end_time
    status = status_detect(event_start, event_end, event.is_work, event.is_finish)
    # Add a scan qrcode log.
    add_qrcode_log(event_id)
    # Check which chatroom is available.

    result = {
        'err_code': 0,
        'content': {'event_status': status,
                    'chatroom_qr': 'fake',
                    'chatroom_name': 'fake',
                    'chatroom_avatar': 'fake',
                    'qr_end_date': 1522454400,
                    }
    }
    return response(result)


_modify_need = (
    'need_fission', 'need_condition_word', 'need_pull_people', 'fission_word_1', 'fission_word_2',
    'condition_word', 'pull_people_word', 'event_title', 'start_time', 'end_time', 'start_index',
    'chatroom_name_protect', 'chatroom_repeat_protect', 'poster_raw', 'start_name')


@app_test.route('/events_modify_word', methods=['POST'])
@para_check(_modify_need, 'token', 'event_id', )
def modify_event_word():
    event_id = request.json.get('event_id')
    para_as_dict = {}
    for i in _modify_need:
        para_as_dict[i] = request.json.get(i)
    # db.session.query(Event).filter(Event.id == event_id).update(para_as_dict)
    # db.session.commit()
    event = BaseModel.fetch_by_id('events', event_id)
    event.from_json(para_as_dict)
    event.save()
    return response({'err_code': 0, 'content': 'SUCCESS'})


@app_test.route('/events_detail', methods=['POST'])
@para_check('token', 'event_id')
def events_detail():
    event_id = request.json.get('event_id')
    event = BaseModel.fetch_by_id('events', event_id)
    if event is None:
        return response({'err_code': -2, 'content': 'No this event.'})
    result = {'err_code': 0}
    content = {}
    content.update({'poster_raw': read_poster_raw(event.poster_raw),
                    'event_title': event.event_title,
                    'alive_qrcode_url': event.alive_qrcode_url,
                    'need_fission': event.need_fission,
                    'need_condition_word': event.need_condition_word,
                    'need_pull_people': event.need_pull_people,
                    'condition_word': event.condition_word,
                    'fission_word_1': event.fission_word_1,
                    'fission_word_2': event.fission_word_2,
                    'pull_people_word': event.pull_people_word,
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    # Add more
                    'chatroom_name_protect': event.chatroom_name_protect,
                    'chatroom_repeat_protect': event.chatroom_repeat_protect,
                    'start_index': event.start_index,
                    'start_name': event.start_name,
                    })
    # Add chatroom info.
    content['chatrooms'] = [
        {'chatroom_avatar': 'fake', 'chatroom_name': 'fake', 'chatroom_status': 1, 'chatroom_member_num': 30}]

    _temp = content.copy()

    for k, v in _temp.items():
        if k in ('start_index',):
            continue
        if v == 1:
            content[k] = True
        if v == 0:
            content[k] = False
    content['event_status'] = status_detect(event.start_time, event.end_time, event.is_work, event.is_finish)
    result['content'] = content
    return response(result)


@app_test.route('/events_list', methods=['POST'])
@para_check('token')
def events_list():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})
    # events = db.session.query(Event).filter(Event.owner == owner).all()
    events = BaseModel.fetch_all('events', '*', BaseModel.where_dict({"owner": owner}))
    result = {'err_code': 0, 'content': []}
    for i in events:
        temp = {}
        today_inc, total_inc = inc_info(i.get_id())
        temp.update({
            'event_id': i.events_id,
            'poster_raw': read_poster_raw(i.poster_raw),
            'event_title': i.event_title,
            'event_status': status_detect(i.start_time, i.end_time, i.is_work, i.is_finish),
            'start_time': i.start_time,
            'end_time': i.end_time,
            # Need another table to search.
            'chatroom_total': 2,  # Just check chatroom list.
            'today_inc': today_inc,
            'total_inc': 0,  # the people of all chatroom.
        })
        result['content'].append(temp)
    return response(result)


def response(body_as_dict):
    """Use make_response or not."""
    response_body = jsonify(body_as_dict)
    return response_body


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


def status_detect(start_time, end_time, is_work, is_finish):
    """Check event status
    1 -> running
    2 -> waiting
    3 -> is over
    """
    if not is_finish:
        return 0
    if not is_work:
        return 3
    now = int(time.time())

    if now < start_time:
        return 2
    elif now > end_time:
        return 3
    return 1


def add_qrcode_log(owner):
    """Add a log."""
    new_log = CM('events_scan_qrcode_info')
    new_log.owner = owner
    new_log.scan_time = int(time.time())
    new_log.save()
    # db.session.add(new_log)
    # db.session.commit()


def inc_info(owner):
    """(today_inc,total_inc)"""
    # logs = db.session.query(ScanQRcode).filter(ScanQRcode.owner == owner).all()
    logs = BaseModel.fetch_all('events_scan_qrcode_info', '*', BaseModel.where_dict({"owner": owner}))
    flag = int(time.time()) - 86400
    today_inc = 0
    all_inc = 0
    for i in logs:
        all_inc += 1
        if i.scan_time > flag:
            today_inc += 1

    return today_inc, all_inc


def to_bytes(obj):
    if isinstance(obj, bytes):
        return obj
    elif isinstance(obj, str):
        return obj.encode()
    elif isinstance(obj, unicode):
        return obj.encode()
    else:
        raise TypeError('Only support (bytes, str). Type:%s' % type(obj))


def to_str(obj):
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, bytes):
        return obj.decode()
    elif isinstance(obj, unicode):
        return obj.decode()
    else:
        raise TypeError('Only support (bytes, str). Type:%s' % type(obj))


def read_poster_raw(_str):
    if not _str:
        return ''
    if os.path.isfile(_str):
        with open(_str, 'rb') as f:
            return to_str(f.read())
    else:
        return to_str(_str)


def new_file_path(path, ext='', start_index=1, end_index=10000):
    if not os.path.isdir(path):
        raise Exception('path must be a directory.')

    if not os.path.exists(path):
        raise Exception('path must be exist.')

    for i in range(start_index, end_index):
        result = os.path.join(path, (str(i) + ext))
        if not os.path.exists(result):
            return result

    raise Exception('Max Length!')
