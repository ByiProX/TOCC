# -*- coding: utf-8 -*-
import os
import time
import base64
import logging
import threading

import requests
import oss2
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
    event_instance = BaseModel.fetch_all('events', '*', BaseModel.where_dict({"owner": owner}))
    if event_instance:
        for i in event_instance:
            if i.is_finish == 0:
                previous_event = BaseModel.fetch_one('events', '*',
                                                     BaseModel.where_dict({"owner": owner, "is_finish": 0}))
                alive_qrcode_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc3bc48b4c40651fd&redirect_uri=http%3a%2f%2ftest2.xuanren360.com%2fchatroom.html&response_type=code&scope=snsapi_userinfo&state={}#wechat_redirect'.format(
                    previous_event.events_id)
                event_id = previous_event.events_id
                return response({'err_code': 0, 'content': {'alive_qrcode_url': alive_qrcode_url,
                                                            'fission_word_1': '嗨！恭喜您即将获取「3点钟无眠区块链」听课资格！ 1.转发以上图片+文字到朋友圈或者100以上群聊中 2.不要屏蔽好友，转发后截图发至本群 3.转发后在本群等待听课即可 分享图片及内容如下 ↓↓↓↓↓ ',
                                                            'fission_word_2': '区块链行业大咖邀请您在4月28日收听课程【3点钟无眠区块链】 名额有限 快扫码入群吧！ ',
                                                            'condition_word': '3点种无眠区块链共同学习赚钱群，现在限时免费获取听课资格，满员开课哦！ ',
                                                            'pull_people_word': '3点种无眠区块链共同学习赚钱群，现在限时免费获取听课资格，满员开课哦！ ',
                                                            'event_id': event_id}})
    # Create base event.

    new_event = CM('events')
    new_event.owner = owner
    new_event.is_finish = 0
    new_event.save()
    # Add QRcode URL.
    previous_event = BaseModel.fetch_one('events', '*',
                                         BaseModel.where_dict({"owner": owner, "is_finish": 0}))
    alive_qrcode_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc3bc48b4c40651fd&redirect_uri=http%3a%2f%2ftest2.xuanren360.com%2fchatroom.html&response_type=code&scope=snsapi_userinfo&state={}#wechat_redirect'.format(
        previous_event.events_id)
    previous_event.alive_qrcode_url = alive_qrcode_url
    previous_event.save()
    # Static word.
    result = {
        'fission_word_1': '嗨！恭喜您即将获取「3点钟无眠区块链」听课资格！ 1.转发以上图片+文字到朋友圈或者100以上群聊中 2.不要屏蔽好友，转发后截图发至本群 3.转发后在本群等待听课即可 分享图片及内容如下 ↓↓↓↓↓ ',
        'fission_word_2': '区块链行业大咖邀请您在4月28日收听课程【3点钟无眠区块链】 名额有限 快扫码入群吧！ ',
        'condition_word': '3点种无眠区块链共同学习赚钱群，现在限时免费获取听课资格，满员开课哦！ ',
        'pull_people_word': '3点种无眠区块链共同学习赚钱群，现在限时免费获取听课资格，满员开课哦！ ',
        'event_id': previous_event.events_id,
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
        client_id = user_info.client_id
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})

    # Check previous init.
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
    # Fix time is float.
    full_event_paras_as_dict['start_time'] = int(full_event_paras_as_dict['start_time'])
    full_event_paras_as_dict['end_time'] = int(full_event_paras_as_dict['end_time'])
    # Check if same start_name already exist.        
    check_events_start_name = BaseModel.fetch_all('events', '*', BaseModel.where_dict({'owner': owner}))
    for i in check_events_start_name:
        if i.start_name == full_event_paras_as_dict['start_name']:
            return response({'err_code': -1, 'content': 'Same start_name already used.'})

    # Create a full event.
    full_event_paras_as_dict['is_finish'] = 1
    full_event_paras_as_dict['enough_chatroom'] = 0
    # True -> 1, False ->0
    full_event_paras_as_dict = true_false_to_10(full_event_paras_as_dict)

    event = BaseModel.fetch_one('events', '*',
                                BaseModel.where_dict({"owner": owner, "is_finish": 0}))
    event_id = event.events_id
    # Fix is_work
    full_event_paras_as_dict.update({'is_work': 1})
    # Save poster raw.
    # [Fix]
    poster_raw = request.json.get('poster_raw')
    if poster_raw:
        try:
            poster_raw = poster_raw.replace('data:image/png;base64,', '')
            img_url = put_img_to_oss(event_id, poster_raw)
        except Exception as e:
            return response({'err_code': -2, 'content': 'Give me base64 poster_raw %s' % e})
        full_event_paras_as_dict['poster_raw'] = img_url
    else:
        full_event_paras_as_dict['poster_raw'] = ''

    event.from_json(full_event_paras_as_dict)

    # Create a chatroom for this event. index = start_index.
    chatroom_nickname = event.start_name + str(event.start_index) + u'群'
    check_bot_username = BaseModel.fetch_one('client_bot_r', '*',
                                             BaseModel.where_dict({'client_id': client_id}))
    if check_bot_username:
        _bot_username = check_bot_username.bot_username
    else:
        return response({'err_code': -3, 'err_info': 'This client does not have bot.'})
    create_chatroom_dict = {
        'bot_username': _bot_username,
        'data': {
            'task': 'create_chatroom',
            "owner": event.owner,
            "chatroom_nickname": chatroom_nickname
        }
    }
    # Try create chatroom.
    try:
        create_chatroom_resp = requests.post('http://ardsvr.xuanren360.com/android/send_message',
                                             json=create_chatroom_dict)
        if dict(create_chatroom_resp.json())['err_code'] == -1:
            return response({'err_code': -3, 'err_info': 'Bot dead.'})
    except Exception as e:
        logger.warning('Create chatroom request error:{}'.format(e))
        return response({'err_code': -3, 'err_info': 'Bot dead:e'})

    # Add chatroom relationship info in events_chatroom.
    events_chatroom = CM('events_chatroom')
    events_chatroom.index = event.start_index
    events_chatroom.chatroomname = 'default'
    events_chatroom.event_id = event.events_id
    events_chatroom.chatroom_nickname = chatroom_nickname
    events_chatroom.roomowner = event.owner

    new_thread = threading.Thread(target=rewrite_events_chatroom,
                                  args=(event.owner, chatroom_nickname, event.events_id))
    new_thread.setDaemon(True)
    new_thread.start()

    # Save at final.
    events_chatroom_save_success = events_chatroom.save()
    event_save_success = event.save()
    if not events_chatroom_save_success or not event_save_success:
        return response(
            {'err_code': -3, 'err_info': 'Save error:%s,%s' % (events_chatroom_save_success, event_save_success)})

    return response({'err_code': 0, 'content': {'event_id': event_id}})


@app_test.route('/events_same_start_name', methods=['POST'])
@para_check('token', 'start_name')
def have_same_start_name():
    # Check owner or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})
    start_name = request.json.get('start_name')
    # Check if same start_name already exist.
    check_events_start_name = BaseModel.fetch_all('events', '*', BaseModel.where_dict({'owner': owner}))
    for i in check_events_start_name:
        if i.start_name == start_name:
            return response({'err_code': 0, 'content': True})

    return response({'err_code': 0, 'content': False})


@app_test.route('/events_delete', methods=['POST'])
@para_check('token', 'event_id')
def disable_events():
    # Check token and event_id.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    owner = user_info.username
    event_id = request.json.get('event_id')
    # Search event.
    # temp_check = db.session.query(Event).filter(Event.owner == owner, Event.id == event_id).first()
    temp_check = BaseModel.fetch_by_id('events', event_id)
    if temp_check is None:
        return response({'err_code': -2, 'content': 'Logical error.'})
    else:
        temp_check.is_work = 0
        temp_check.save()
        return response({'err_code': 0, 'content': 'SUCCESS'})


@app_test.route('/events_qrcode', methods=['POST'])
@para_check('event_id', 'code', 'app_name')
def get_events_qrcode():
    """Get event base info (for qrcode)."""
    event_id = request.json.get('event_id')
    user_login = UserLogin(request.json.get('code'), request.json.get('app_name'))
    status, user_info = user_login.get_user_token()
    user_nickname = user_info.nick_name

    # Handle.
    event = BaseModel.fetch_by_id('events', event_id)
    if event is None:
        return response({'err_code': -3, 'err_info': 'Fake event_id'})
    # Use event_id search chatroom list, then get a prepared chatroom
    # and return its chatroomname.
    event_start = event.start_time
    event_end = event.end_time
    status = status_detect(event_start, event_end, event.is_work, event.is_finish, event.enough_chatroom)
    # Add a scan qrcode log.
    add_qrcode_log(event_id)
    # Check which chatroom is available.
    chatroom_list = BaseModel.fetch_all('events_chatroom', '*', BaseModel.where_dict({'event_id': event_id}))
    # Not a available chatroom, so it is in base create status.
    in_base_status = True
    for i in chatroom_list:
        if i.chatroomname != 'default':
            in_base_status = False
    if in_base_status:
        return response({'err_code': 0,
                         'content': {'event_status': 4, 'chatroom_qr': '', 'chatroom_name': '', 'chatroom_avatar': '',
                                     'qr_end_date': ''}})

    chatroom_dict = {}
    chatroomname_list = []
    for i in chatroom_list:
        chatroom_info = BaseModel.fetch_one('a_chatroom', '*', BaseModel.where_dict({'chatroomname': i.chatroomname}))
        if chatroom_info:
            chatroom_dict[i.chatroomname] = (
                len(chatroom_info.memberlist.split(';')), chatroom_info.qrcode, chatroom_info.nickname_real,
                chatroom_info.avatar_url,
                chatroom_info.update_time)
            chatroomname_list.append(i.chatroomname)

    if chatroom_dict:
        # Have enough chatroom. if open repeat protect, check this one whether already exist in a chatroom.
        # TODO
        if event.chatroom_repeat_protect and False:
            for i in chatroomname_list:
                this_chatroom = BaseModel.fetch_one('a_chatroom', 'memberlist',
                                                    BaseModel.where_dict({'chatroomname': i}))
                member_list = this_chatroom.memberlist.split(';')

        for k, v in chatroom_dict.items():
            if v[0] < 6:
                result = {
                    'err_code': 0,
                    'content': {'event_status': status,
                                'chatroom_qr': v[1],
                                'chatroom_name': v[2],
                                'chatroom_avatar': v[3],
                                'qr_end_date': v[4],
                                }
                }
                return response(result)
    """Do not have a chatroom < 100, create one."""
    event.enough_chatroom = 0
    owner = event.owner
    this_client_member = BaseModel.fetch_one('client_member', '*', BaseModel.where_dict({'username': owner}))
    _client_id = this_client_member.client_id
    print('--client_id:',_client_id)
    event.save()
    start_name = event.start_name
    new_thread = threading.Thread(target=create_chatroom_for_scan, args=(event_id, _client_id, owner, start_name))
    new_thread.setDaemon(True)
    new_thread.start()

    return response({'err_code': 0,
                     'content': {'event_status': 4, 'chatroom_qr': '', 'chatroom_name': '', 'chatroom_avatar': '',
                                 'qr_end_date': ''}})


@app_test.route('/events_modify_word', methods=['POST'])
@para_check('token', 'event_id', )
def modify_event_word():
    # Check owner or return.
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})

    _modify_need = (
        'need_fission', 'need_condition_word', 'need_pull_people', 'fission_word_1', 'fission_word_2',
        'condition_word', 'pull_people_word', 'event_title', 'start_time', 'end_time',
        'chatroom_name_protect', 'poster_raw', 'start_name')
    event_id = request.json.get('event_id')
    para_as_dict = {}

    values_as_dict = dict(request.json)

    for k, v in values_as_dict.items():
        if k in _modify_need:
            para_as_dict[k] = v

    para_as_dict = true_false_to_10(para_as_dict)

    event = BaseModel.fetch_by_id('events', event_id)
    if event is None:
        return response({'err_code': -3, 'err_info': 'Wrong event_id.'})

    # Same start_name check.
    new_start_name = request.json.get('start_name')
    if event.start_name == new_start_name:
        # Don't modify start_name.
        pass
    else:
        all_event = BaseModel.fetch_all('events', '*', BaseModel.where_dict({'owner': owner}))
        for i in all_event:
            if i.start_name == new_start_name:
                return response({'err_code': -3, 'err_info': 'Start name already exist.'})

    # Save poster_raw
    poster_raw = para_as_dict.get('poster_raw')
    if poster_raw:
        if 'http://ywbdposter.oss-cn-beijing.aliyuncs.com' not in poster_raw:
            try:
                poster_raw = poster_raw.replace('data:image/png;base64,', '')
                img_url = put_img_to_oss(event_id, poster_raw)
            except Exception as e:
                return response({'err_code': -2, 'content': 'Give me base64 poster_raw %s' % e})
            para_as_dict['poster_raw'] = img_url
    else:
        para_as_dict['poster_raw'] = ''

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
    content.update({'poster_raw': event.poster_raw,
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
    content_chatrooms = []
    event_chatroom_list = BaseModel.fetch_all('events_chatroom', '*',
                                              BaseModel.where_dict({'event_id': event.events_id}))
    for i in event_chatroom_list:
        if i.chatroomname != 'default':
            this_chatroom = BaseModel.fetch_one('a_chatroom', '*',
                                                BaseModel.where_dict({'chatroomname': i.chatroomname}))
            _result = {'chatroom_avatar': this_chatroom.avatar_url, 'chatroom_name': i.chatroom_nickname,
                       'chatroom_status': 1,
                       'chatroom_member_num': len(this_chatroom.memberlist.split(';'))}
            content_chatrooms.append(_result)
    content['chatrooms'] = content_chatrooms

    _temp = content.copy()

    for k, v in _temp.items():
        if k in ('start_index',):
            continue
        if v == 1:
            content[k] = True
        if v == 0:
            content[k] = False

    content['event_status'] = status_detect(event.start_time, event.end_time, event.is_work, event.is_finish,
                                            event.enough_chatroom)
    result['content'] = content

    return response(result)


@app_test.route('/events_list', methods=['POST'])
@para_check('token', )
def events_list():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    try:
        owner = user_info.username
    except AttributeError:
        return response({'err_code': -2, 'content': 'User token error.'})
    events = BaseModel.fetch_all('events', '*', BaseModel.where_dict({"owner": owner}))

    result = {'err_code': 0, 'content': []}
    for i in events:
        temp = {}
        today_inc, all_inc = inc_info(i.get_id())
        # Get chatroom info.
        event_chatroom_list = BaseModel.fetch_all('events_chatroom', '*',
                                                  BaseModel.where_dict({"event_id": i.events_id}))
        total_inc = 0
        chatroom_total = 0
        for j in event_chatroom_list:
            if j.chatroomname != 'default':
                chatroom_total += 1
                this_chatroom = BaseModel.fetch_one('a_chatroom', '*',
                                                    BaseModel.where_dict({'chatroomname': j.chatroomname}))

                if this_chatroom:
                    if this_chatroom.memberlist:
                        total_inc += len(this_chatroom.memberlist.split(';'))
                else:
                    logger.warning('Can not find this chatroom:{}'.format(j.chatroomname))

        temp.update({
            'event_id': i.events_id,
            'poster_raw': i.poster_raw,
            'event_title': i.event_title,
            'event_status': status_detect(i.start_time, i.end_time, i.is_work, i.is_finish, i.enough_chatroom),
            'start_time': i.start_time,
            'end_time': i.end_time,
            # Need another table to search.
            'chatroom_total': chatroom_total,
            'today_inc': today_inc,
            'total_inc': total_inc,  # the people of all chatroom.
        })
        result['content'].append(temp)
    result['content'].reverse()

    return response(result)


def rewrite_events_chatroom(roomowner, chatroom_nickname, event_id):
    print('Rewrite running')
    flag = True
    # Get roomowner's bot_username
    client_member = BaseModel.fetch_one('client_member', '*', BaseModel.where_dict({'username': roomowner}))
    client_id = client_member.client_id
    client_bot_r = BaseModel.fetch_one('client_bot_r', '*', BaseModel.where_dict({'client_id': client_id}))
    bot_username = client_bot_r.bot_username

    while flag:
        time.sleep(2)
        chatroom = BaseModel.fetch_one('a_chatroom', '*',
                                       BaseModel.where_dict(
                                           {'roomowner': bot_username, 'nickname_real': chatroom_nickname}))
        if chatroom is not None:
            chatroomname = chatroom.chatroomname
            events_chatroom = BaseModel.fetch_one('events_chatroom', '*', BaseModel.where_dict(
                {'roomowner': roomowner, 'chatroom_nickname': chatroom_nickname}))
            events_chatroom.chatroomname = chatroomname
            events_chatroom.save()
            # Make events have enough chatroom.
            event = BaseModel.fetch_by_id('events', event_id)
            event.enough_chatroom = 1
            event.save()
            flag = False
    print('Rewrite ok.')
    return ' '


def create_chatroom_for_scan(event_id, __client_id, owner, start_name):
    """create_chatroom_for_scan"""
    print("Running create_chatroom_for_scan")
    """Get previous index"""
    previous_chatroom_list = BaseModel.fetch_all('events_chatroom', '*', BaseModel.where_dict({'event_id': event_id}))
    previous_index_list = []
    for i in previous_chatroom_list:
        previous_index_list.append(i.index)
    previous_index_list.sort()

    now_index = previous_index_list[-1] + 1
    print('--now_index',now_index)
    # Create a chatroom for this event. index = start_index.
    chatroom_nickname = start_name + str(now_index) + u'群'
    _bot_username = BaseModel.fetch_one('client_bot_r', '*',
                                        BaseModel.where_dict({'client_id': __client_id}))
    print('--bot_username',_bot_username)
    if _bot_username:
        __bot_username = _bot_username.bot_username
    else:
        logger.warning('Error when create_chatroom_for_scan')
        return 0

    create_chatroom_dict = {
        'bot_username': __bot_username,
        'data': {
            'task': 'create_chatroom',
            "owner": owner,
            "chatroom_nickname": chatroom_nickname
        }
    }
    try:
        create_chatroom_resp = requests.post('http://ardsvr.xuanren360.com/android/send_message',
                                             json=create_chatroom_dict)
        logger.info('create_chatroom_resp(for scan):', create_chatroom_resp)
    except Exception as e:
        logger.warning('Create chatroom request error:{}'.format(e))
    # Add chatroom info in relationship.
    events_chatroom = CM('events_chatroom')
    events_chatroom.index = now_index
    events_chatroom.chatroomname = 'default'
    events_chatroom.event_id = event_id
    events_chatroom.chatroom_nickname = chatroom_nickname
    events_chatroom.roomowner = owner

    # Update chatroomname.
    rewrite_events_chatroom(owner, chatroom_nickname, event_id)
    return ' '


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


def status_detect(start_time, end_time, is_work, is_finish, chatroom_enough):
    """Check event status
    0 -> not finish
    1 -> running
    2 -> waiting
    3 -> is over
    4 -> chatroom not created
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

    if not chatroom_enough:
        return 4

    return 1


def add_qrcode_log(owner):
    """Add a log."""
    new_log = CM('events_scan_qrcode_info')
    new_log.owner = owner
    new_log.scan_time = int(time.time())
    new_log.save()


def inc_info(owner):
    """(today_inc,total_inc)"""
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
        return obj
    else:
        raise TypeError('Only support (bytes, str). Type:%s' % type(obj))


def true_false_to_10(data_as_dict, exc_list=()):
    for k, v in data_as_dict.items():
        if k in exc_list:
            continue
        if v is True:
            data_as_dict[k] = 1
        elif v is False:
            data_as_dict[k] = 0

    return data_as_dict


def _10_to_true_false(data_as_dict, exc_list=()):
    for k, v in data_as_dict.items():
        if k in exc_list:
            continue
        if v == 1:
            data_as_dict[k] = True
        elif v == 0:
            data_as_dict[k] = False

    return data_as_dict


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


def open_chatroom_name_protect():
    while True:
        time.sleep(100)
        event_list = BaseModel.fetch_all('events', '*')
        for i in event_list:
            if i.chatroom_name_protect:
                event_chatroom_list = BaseModel.fetch_all('events_chatroom', '*',
                                                          BaseModel.where_dict({'event_id': i.events_id}))
                for j in event_chatroom_list:
                    if j.chatroomname != 'default':
                        now_chatroom_info = BaseModel.fetch_one('a_chatroom', '*',
                                                                BaseModel.where_dict({'chatroomname': j.chatroomname}))
                        if now_chatroom_info.nickname_real != j.chatroom_nickname:
                            this_client_id = BaseModel.fetch_one('client_member', '*',
                                                                 BaseModel.where_dict({'username': j.roomowner}))
                            _bot_username = BaseModel.fetch_one('client_bot_r', '*',
                                                                BaseModel.where_dict(
                                                                    {'client_id': this_client_id})).bot_username
                            result = {'bot_username': _bot_username,
                                      'data': {
                                          "task": "update_chatroom_nick",
                                          "chatroomname": j.chatroomname,
                                          "chatroomnick": j.chatroom_nickname,
                                      }}
                            requests.post('http://ardsvr.xuanren360.com/android/send_message', json=result)


def event_chatroom_send_word():
    print('event_chatroom_send_word Running.')
    # Base status.
    chatroom_status_dict = dict()
    chatroom_task_status_dict = dict()
    event_list = BaseModel.fetch_all('events', '*',
                                     BaseModel.where_dict({'is_finish': 1, 'is_work': 1, 'enough_chatroom': 1}))
    for event in event_list:
        event_id = event.events_id
        # Get all chatroom in this event.
        chatroom_list = BaseModel.fetch_all('events_chatroom', '*', BaseModel.where_dict({'event_id': event_id}))
        for chatroom in chatroom_list:
            if chatroom.chatroomname == 'default':
                continue
            # Update status
            this_chatroom = BaseModel.fetch_one('a_chatroom', 'memberlist',
                                                BaseModel.where_dict({'chatroomname': chatroom.chatroomname}))

            if not this_chatroom:
                logger.warning('member_count ERROR!!! Can not find this_chatroom:%s' % chatroom.chatroomname)
                member_count = 0
            else:
                member_count = len(this_chatroom.memberlist.split(';'))

            chatroom_status_dict[chatroom.chatroomname] = member_count
            chatroom_task_status_dict[chatroom.chatroomname] = [0, 0, 0, 0]  # 30 50 80 100 task-status

    def send_message(_bot_username, to, _type, content):
        result = {'bot_username': _bot_username,
                  'data': {
                      "task": "send_message",
                      "to": to,
                      "type": _type,
                      "content": content,
                  }}
        resp = requests.post('http://ardsvr.xuanren360.com/android/send_message', json=result)
        if dict(resp.json())['err_code'] == -1:
            logger.warning('event_chatroom_send_word ERROR,because bot dead!')

    def get_owner_bot_username(roomowner):
        # Get roomowner's bot_username
        client_member = BaseModel.fetch_one('client_member', '*', BaseModel.where_dict({'username': roomowner}))
        _client_id = client_member.client_id
        client_bot_r = BaseModel.fetch_one('client_bot_r', '*', BaseModel.where_dict({'client_id': _client_id}))
        __bot_username = client_bot_r.bot_username

        return __bot_username

    while True:
        time.sleep(0.5)
        # Get all event.
        event_list = BaseModel.fetch_all('events', '*',
                                         BaseModel.where_dict({'is_finish': 1, 'is_work': 1, 'enough_chatroom': 1}))
        previous_chatroom_status_dict = chatroom_status_dict.copy()
        for event in event_list:
            event_id = event.events_id
            # Get all chatroom in this event.
            chatroom_list = BaseModel.fetch_all('events_chatroom', '*', BaseModel.where_dict({'event_id': event_id}))
            for chatroom in chatroom_list:
                if chatroom.chatroomname == 'default':
                    continue
                # Update status
                this_chatroom = BaseModel.fetch_one('a_chatroom', 'memberlist',
                                                    BaseModel.where_dict({'chatroomname': chatroom.chatroomname}))

                if not this_chatroom:
                    logger.warning('member_count ERROR!!! Can not find this_chatroom:%s' % chatroom.chatroomname)
                    member_count = 0
                else:
                    member_count = len(this_chatroom.memberlist.split(';'))

                chatroom_status_dict[chatroom.chatroomname] = member_count
                need_fission, need_condition_word, need_pull_people = event.need_fission, event.need_condition_word, event.need_pull_people
                # If previous chatroom list also have same chatroomname.
                if previous_chatroom_status_dict.get(chatroom.chatroomname):
                    previous_chatroom_member_count = previous_chatroom_status_dict[chatroom.chatroomname]
                    now_chatroom_member_count = chatroom_status_dict[chatroom.chatroomname]
                    if now_chatroom_member_count > previous_chatroom_member_count and need_fission:
                        # Send welcome message.
                        this_bot_username = get_owner_bot_username(event.owner)
                        send_message(this_bot_username, chatroom.chatroomname, 1, event.fission_word_1)
                        send_message(this_bot_username, chatroom.chatroomname, 1, event.fission_word_2)
                    if now_chatroom_member_count in (30, 50, 80) and need_pull_people:
                        # Change chatroomnotice.
                        pass
                    if now_chatroom_member_count == 100 and need_condition_word:
                        # Full people notice.
                        pass


def put_img_to_oss(file_name, data_as_string):
    img_name = str(file_name) + '.jpg'

    endpoint = 'oss-cn-beijing.aliyuncs.com'
    auth = oss2.Auth('LTAIfwRTXLl6vMbX', 'kvSS9E4Ty7nvHHlGukaknJUtfICuen')
    bucket = oss2.Bucket(auth, endpoint, 'ywbdposter')
    bucket.put_object(img_name, base64.b64decode(data_as_string))

    return 'http://ywbdposter.oss-cn-beijing.aliyuncs.com/' + img_name


new_thread_2 = threading.Thread(target=event_chatroom_send_word)
new_thread_2.setDaemon(True)
new_thread_2.start()

new_thread_3 = threading.Thread(target=open_chatroom_name_protect)
new_thread_3.setDaemon(True)
new_thread_3.start()


def events_chatroomname_check():
    chatrooms = BaseModel.fetch_all('events_chatroom', '*', BaseModel.where_dict({'chatroomname': 'default'}))

    for i in chatrooms:
        new_thread = threading.Thread(target=rewrite_events_chatroom,
                                      args=(i.roomowner, i.chatroom_nickname, i.event_id))
        new_thread.setDaemon(True)
        new_thread.start()

# events_chatroomname_check()
