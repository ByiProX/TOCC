# -*- coding: utf-8 -*-

import logging
import time
import json

from decimal import Decimal
from flask import request

from core_v2.user_core import UserLogin
from models.android_db_models import AContact, AMember
from models.chatroom_member_models import ChatroomInfo, UserChatroomR, ChatroomOverview, ChatroomStatistic, \
    ChatroomActive
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from configs.config import SUCCESS, main_api_v2, rds, db, DEFAULT_PAGE, DEFAULT_PAGE_SIZE, ERR_INVALID_PARAMS, \
    ERR_WRONG_ITEM, \
    SCOPE_WEEK, SCOPE_ALL, USER_CHATROOM_R_PERMISSION_1, Chatroom, UserQunR

from models_v2.base_model import *

import datetime

logger = logging.getLogger('main')


def modelList2Arr(mlist):
    ret = []
    if mlist:
        for li in mlist:
            ret.append(li.to_json())
    return ret


def getGrouplist(client_id):
    ret = []
    if client_id:
        dataList = BaseModel.fetch_all('client_group_r', ['group_name', 'group_id', 'status'],
                                        BaseModel.where("=", "client_id", client_id))
        return modelList2Arr(dataList)


# chatroomnames must array
def getQunInfo(chatroomnames):
    ret = {}
    if chatroomnames:
        qunInfo = BaseModel.fetch_all('a_chatroom', ['chatroomname', 'nickname','member_count', 'avatar_url'],BaseModel.where("in", "chatroomname", chatroomnames))
        if (qunInfo):
            for qf in qunInfo:
                _qfjson = qf.to_json() 
                ret[_qfjson["chatroomname"]] = _qfjson
    return ret


def getTimeStamp(d_diff = 0):
    day_diff = str(datetime.date.today() - datetime.timedelta(days = d_diff))
    time_arr = time.strptime(str(day_diff), "%Y-%m-%d")
    return int(time.mktime(time_arr))


def getClientQunWithGroup(client_id, group_id, page = 1, pagesize = 30, order = ''):
    ret = []
    if group_id:
        _where = ["and", ["=", "client_id", client_id], ["=", "group_id", group_id]]
        _where = BaseModel.where_dict(_where)
        qunList = BaseModel.fetch_all('client_qun_r', ['chatroomname', 'group_id', 'group_info', 'status'], _where,
                                      page = 1, pagesize = pagesize, orderBy = order)
        return modelList2Arr(qunList)
 

@main_api_v2.route('/statistics_chatroomone', methods = ['POST'])
def statistics_chatroomone():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)
    chatroomname = request.json.get('chatroomname')
    if not chatroomname:
        return make_response(ERR_INVALID_PARAMS)
    data = BaseModel.fetch_one('a_chatroom', '*', BaseModel.where("=", "chatroomname", chatroomname))
    data = data.to_json()
    return make_response(SUCCESS, chatroominfo = data)


# 根据group id 获取群list
@main_api_v2.route('/statistics_chatroom_qun', methods = ['POST'])
def chatroom_statistics_chatroom_qun():
    verify_json()
    group_id = request.json.get('group_id')
    if not group_id:
        return make_response(ERR_INVALID_PARAMS)

    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    page = request.json.get('page', 1)
    order = request.json.get('order', '')
    pagesize = request.json.get('pagesize', 30)
    qunList = getClientQunWithGroup(user_info.client_id, group_id, page, pagesize, order)
    return make_response(SUCCESS, chatroom_group_qun = qunList)


# 获取 group list
@main_api_v2.route('/statistics_chatroom_group', methods = ['POST'])
def chatroom_statistics_chatroom_group():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)
    groupList = getGrouplist(user_info.client_id)
    return make_response(SUCCESS, chatroom_group = groupList)


@main_api_v2.route('/statistics_chatroom', methods = ['POST'])
def chatroom_statistics_chatroom():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # group_id 群分组ID ， cache key =  dateType_clientId_groupId,
    # cache value= {time():data}  cache 10分钟

    is_active = request.json.get('is_active', True)
    group_id = request.json.get('group_id', '')
    chatroomname_list = []
    if group_id:
        cache_key = 'c_' + group_id
        # 这里需要根据groupId 取 qunID list，或者前端post过来 qunID list
        qunList = getClientQunWithGroup(user_info.client_id, group_id)
        for qli in qunList:
            chatroomname_list.append(qli['chatroomname'])

    # date_type=1 今日实时，每10分钟计算一次，cache 10分钟
    # date_type=2 昨日，从daily取，cache10分钟
    # date_type3=7日，从daily计算过去7天，cache 10分钟
    # date_type4=30日，从daily计算过去30天，cache 10分钟
    # date_type=5 全部，从total表取，cache10分钟
    #   cache key=  dateType_clientId, cache value= {time():data}
    date_type = request.json.get('date_type', 1)
    run_hour = ''
    table = 'statistics_chatroom_hour'
    _timestamp = int(time.time())
    _where = []
    #if (date_type == 1):
    #    run_hour = int(time.strftime('%H', time.localtime(time.time())))
    #    last_update_time = _timestamp - 600
    #    if (run_hour == 0):
    #        return make_response(SUCCESS, chatroom_list = [], last_update_time = last_update_time)
    #    _where = ["and", ["<=", "run_hour", run_hour], ["=", "client_id", user_info.client_id],
    #              ["in", "chatroomname", chatroomname_list]]
    if (date_type == 1):
        timestamp_diff = getTimeStamp(0)
        last_update_time = timestamp_diff + 600
        # _where ={"date":timestamp_diff,"client_id":user_info.client_id}
        _where = ["and", ["=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
        table = 'statistics_chatroom_daily'
    elif (date_type == 2):
        timestamp_diff = getTimeStamp(1)
        last_update_time = timestamp_diff + 600
        # _where ={"date":timestamp_diff,"client_id":user_info.client_id}
        _where = ["and", ["=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
        table = 'statistics_chatroom_daily'
    elif (date_type == 3):
        timestamp_diff = getTimeStamp(7)
        last_update_time = getTimeStamp(1) + 600
        table = 'statistics_chatroom_daily'
        _where = ["and", [">=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
    elif (date_type == 4):
        timestamp_diff = getTimeStamp(30)
        last_update_time = getTimeStamp(1) + 600
        table = 'statistics_chatroom_daily'
        _where = ["and", [">=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
    elif (date_type == 5):
        last_update_time = getTimeStamp(1) + 1200
        table = 'statistics_chatroom_total'
        # _where ={"client_id":user_info.client_id}
        _where = ["and", ["=", "client_id", user_info.client_id], ["in", "chatroomname", chatroomname_list]]

    cache_key = '_st' + str(date_type) + '_' + str(user_info.client_id)

    # 群ID，cache key = dateType_clientId_chatroomname ,cache 10分钟
    chatroomname = request.json.get('chatroomname')
    if chatroomname:
        _where = {"chatroomname": chatroomname, "client_id": user_info.client_id}
        cache_key = cache_key + '_' + chatroomname

    page = request.json.get('page', 1)
    pagesize = request.json.get('pagesize', 30)
    cache_key = cache_key + '_p' + str(page)

    # 规则是 active_count 是字段名，去掉count，变成 active_asc or active_desc
    order = request.json.get('order')
    if order:
        cache_key = cache_key + '_' + order
        order = order.split('_')
        order = order[0] + '_count' + ' ' + order[1]

    cacheData = rds.get(cache_key)
    if cacheData:
        print "cache hit"
        cacheData = json.loads(cacheData)
        for cd in cacheData:
            return make_response(SUCCESS, chatroom_list = cacheData[cd], last_update_time = cd)

    _where = BaseModel.where_dict(_where)

    print "------_where:::-----------\n", _where, order, "-----------------\n"

    chatroom_statis = BaseModel.fetch_all(table, '*', _where, page = 1, pagesize = pagesize, orderBy = order)
    chatroom_json_list = []
    if (len(chatroom_statis) < 1):
        return make_response(SUCCESS, chatroom_list = [], last_update_time = last_update_time)

    chatroomnames = []
    for st in chatroom_statis:
        _stjson = st.to_json_full()
        print _stjson
        chatroomnames.append(_stjson['chatroomname'])
        chatroom_json_list.append(_stjson)

    qunInfo = getQunInfo(chatroomnames)
    print "==========\n", qunInfo, "============\n"

    if (len(qunInfo) > 0):
        for ctlist in chatroom_json_list:
            if qunInfo.has_key(ctlist['chatroomname']):
                ctlist.update(qunInfo[ctlist['chatroomname']]) 

    if (len(chatroom_json_list) > 0):
        rds.set(cache_key, json.dumps({last_update_time: chatroom_json_list}))
        rds.expire(cache_key, 10)

    if not is_active:
        uqr_list = BaseModel.fetch_all(UserQunR, "*", where_clause = BaseModel.where_dict(["and", ["=", "client_id", user_info.client_id], ["not in", "chatroomname", chatroomnames]]), page = 1, pagesize = pagesize)
        chatroomname_list = [r.chatroomname for r in uqr_list]
        qunInfo = BaseModel.fetch_all('a_chatroom', ['chatroomname', 'nickname','member_count', 'avatar_url'],
                                      BaseModel.where("in", "chatroomname", chatroomname_list))
        chatroom_json_list = []
        for chatroom in qunInfo:
            chatroom_json = chatroom.to_json_full()
            chatroom_json_list.append(chatroom_json)
        return make_response(SUCCESS, chatroom_list = chatroom_json_list, last_update_time = last_update_time)
    
    ret_chatroom = sumList(chatroom_json_list)
    return make_response(SUCCESS, chatroom_list = ret_chatroom, last_update_time = last_update_time)




def sumList(chatroomlist):
    arr = []
    ret = {}
    if chatroomlist:
        for cm in chatroomlist: 
            if ret.has_key(cm['chatroomname']): 
               
                try:
                    ret[cm['chatroomname']]['active_count'] = ret[cm['chatroomname']]['active_count'] + cm['chatroomname']['active_count']
                except: 
                    print 'err'
                try:
                    ret[cm['chatroomname']]['at_count'] = ret[cm['chatroomname']]['at_count'] + cm['chatroomname']['at_count']
                except: 
                    print 'err'
                try: 
                    ret[cm['chatroomname']]['speak_count'] = ret[cm['chatroomname']]['speak_count'] + cm['chatroomname']['speak_count']
                except:  
                    print 'err'
                try: 
                    ret[cm['chatroomname']]['in_count'] = ret[cm['chatroomname']]['in_count'] + cm['chatroomname']['in_count']
                except: 
                    print 'err'
                try: 
                    ret[cm['chatroomname']]['out_count'] = ret[cm['chatroomname']]['out_count'] + cm['chatroomname']['out_count']
                except: 
                    print 'err'
                
            else:
                ret[cm['chatroomname']] = cm
    print "ret:;------------------",ret,"\n\n"
    for i in ret:
        arr.append(ret[i])
    return arr




@main_api_v2.route("/get_non_active_chatroom_list", methods = ['POSt'])
def get_non_active_chatroom_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # group_id 群分组ID ， cache key =  dateType_clientId_groupId,
    # cache value= {time():data}  cache 10分钟

    is_active = request.json.get('is_active', True)
    group_id = request.json.get('group_id', '')
    chatroomname_list = []
    if group_id:
        cache_key = 'c_' + group_id
        # 这里需要根据groupId 取 qunID list，或者前端post过来 qunID list
        qunList = getClientQunWithGroup(user_info.client_id, group_id)
        for qli in qunList:
            chatroomname_list.append(qli['chatroomname'])

    # date_type=1 今日实时，每10分钟计算一次，cache 10分钟
    # date_type=2 昨日，从daily取，cache10分钟
    # date_type3=7日，从daily计算过去7天，cache 10分钟
    # date_type4=30日，从daily计算过去30天，cache 10分钟
    # date_type=5 全部，从total表取，cache10分钟
    #   cache key=  dateType_clientId, cache value= {time():data}
    date_type = request.json.get('date_type', 1)
    run_hour = ''
    table = 'statistics_chatroom_hour'
    _timestamp = int(time.time())
    _where = []
    # if (date_type == 1):
    #    run_hour = int(time.strftime('%H', time.localtime(time.time())))
    #    last_update_time = _timestamp - 600
    #    if (run_hour == 0):
    #        return make_response(SUCCESS, chatroom_list = [], last_update_time = last_update_time)
    #    _where = ["and", ["<=", "run_hour", run_hour], ["=", "client_id", user_info.client_id],
    #              ["in", "chatroomname", chatroomname_list]]
    if (date_type == 1):
        timestamp_diff = getTimeStamp(0)
        last_update_time = timestamp_diff + 600
        # _where ={"date":timestamp_diff,"client_id":user_info.client_id}
        _where = ["and", ["=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
        table = 'statistics_chatroom_daily'
    elif (date_type == 2):
        timestamp_diff = getTimeStamp(1)
        last_update_time = timestamp_diff + 600
        # _where ={"date":timestamp_diff,"client_id":user_info.client_id}
        _where = ["and", ["=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
        table = 'statistics_chatroom_daily'
    elif (date_type == 3):
        timestamp_diff = getTimeStamp(7)
        last_update_time = getTimeStamp(1) + 600
        table = 'statistics_chatroom_daily'
        _where = ["and", [">=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
    elif (date_type == 4):
        timestamp_diff = getTimeStamp(30)
        last_update_time = getTimeStamp(1) + 600
        table = 'statistics_chatroom_daily'
        _where = ["and", [">=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
    elif (date_type == 5):
        last_update_time = getTimeStamp(1) + 1200
        table = 'statistics_chatroom_total'
        # _where ={"client_id":user_info.client_id}
        _where = ["and", ["=", "client_id", user_info.client_id], ["in", "chatroomname", chatroomname_list]]

    _where = BaseModel.where_dict(_where)

    page = request.json.get('page', 1)
    pagesize = request.json.get('pagesize', 30)

    chatroom_statis = BaseModel.fetch_all(table, '*', _where)
    chatroom_json_list = []
    chatroomnames = [r.chatroomname for r in chatroom_statis]
    uqr_list = BaseModel.fetch_all(UserQunR, "*", where_clause = BaseModel.where_dict(
        ["and", ["=", "client_id", user_info.client_id], ["not in", "chatroomname", chatroomnames]]), page = 1, pagesize = pagesize)
    chatroomname_list = [r.chatroomname for r in uqr_list]
    qunInfo = BaseModel.fetch_all('a_chatroom', ['chatroomname', 'nickname', 'member_count', 'avatar_url'],
                                  BaseModel.where("in", "chatroomname", chatroomname_list))
    for chatroom in qunInfo:
        chatroom_json = chatroom.to_json_full()
        chatroom_json_list.append(chatroom_json)
    return make_response(SUCCESS, chatroom_list = chatroom_json_list, last_update_time = last_update_time)


@main_api_v2.route('/get_active_chatroom_count', methods = ['POST'])
def get_active_chatroom_count():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    # group_id 群分组ID ， cache key =  dateType_clientId_groupId,
    # cache value= {time():data}  cache 10分钟

    group_id = request.json.get('group_id', '')
    chatroomname_list = []
    _where = []
    if group_id:
        cache_key = 'c_' + group_id
        # 这里需要根据groupId 取 qunID list，或者前端post过来 qunID list
        qunList = getClientQunWithGroup(user_info.client_id, group_id)
        for qli in qunList:
            chatroomname_list.append(qli['chatroomname'])

    # date_type=1 今日实时，每10分钟计算一次，cache 10分钟
    # date_type=2 昨日，从daily取，cache10分钟
    # date_type3=7日，从daily计算过去7天，cache 10分钟
    # date_type4=30日，从daily计算过去30天，cache 10分钟
    # date_type=5 全部，从total表取，cache10分钟
    #   cache key=  dateType_clientId, cache value= {time():data}
    date_type = request.json.get('date_type', 1)
    table = 'statistics_chatroom_hour'
    # if (date_type == 1):
    #    run_hour = int(time.strftime('%H', time.localtime(time.time())))
    #    last_update_time = _timestamp - 600
    #    if (run_hour == 0):
    #        return make_response(SUCCESS, chatroom_list = [], last_update_time = last_update_time)
    #    _where = ["and", ["<=", "run_hour", run_hour], ["=", "client_id", user_info.client_id],
    #              ["in", "chatroomname", chatroomname_list]]
    if (date_type == 1):
        timestamp_diff = getTimeStamp(0)
        last_update_time = timestamp_diff + 600
        # _where ={"date":timestamp_diff,"client_id":user_info.client_id}
        _where = ["and", ["=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
        table = 'statistics_chatroom_daily'
    elif (date_type == 2):
        timestamp_diff = getTimeStamp(1)
        last_update_time = timestamp_diff + 600
        # _where ={"date":timestamp_diff,"client_id":user_info.client_id}
        _where = ["and", ["=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
        table = 'statistics_chatroom_daily'
    elif (date_type == 3):
        timestamp_diff = getTimeStamp(7)
        last_update_time = getTimeStamp(1) + 600
        table = 'statistics_chatroom_daily'
        _where = ["and", [">=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
    elif (date_type == 4):
        timestamp_diff = getTimeStamp(30)
        last_update_time = getTimeStamp(1) + 600
        table = 'statistics_chatroom_daily'
        _where = ["and", [">=", "date", timestamp_diff], ["=", "client_id", user_info.client_id],
                  ["in", "chatroomname", chatroomname_list]]
    elif (date_type == 5):
        last_update_time = getTimeStamp(1) + 1200
        table = 'statistics_chatroom_total'
        # _where ={"client_id":user_info.client_id}
        _where = ["and", ["=", "client_id", user_info.client_id], ["in", "chatroomname", chatroomname_list]]

    chatroom_statis = BaseModel.fetch_all(table, '*', where_clause = BaseModel.where_dict(_where))
    chatroomnames = [r.chatroomname for r in chatroom_statis]
    print "chatroomnames", chatroomnames
    active_chatroom_count = len(chatroom_statis)
    non_active_chatroom_count = BaseModel.count(UserQunR, where_clause = BaseModel.where_dict(["and", ["=", "client_id", user_info.client_id], ["not in", "chatroomname", chatroomnames]]))
    # total_count = BaseModel.count(UserQunR, where_clause = BaseModel.where_dict({"client_id": user_info.client_id}))
    # non_active_chatroom_count = total_count - active_chatroom_count

    return make_response(SUCCESS, active_chatroom_count = active_chatroom_count, non_active_chatroom_count = non_active_chatroom_count)
