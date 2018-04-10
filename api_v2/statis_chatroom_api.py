# -*- coding: utf-8 -*-

import logging
import time
import datetime
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
    SCOPE_WEEK, SCOPE_ALL, USER_CHATROOM_R_PERMISSION_1
from utils.u_time import get_time_window_by_scope, datetime_to_timestamp_utc_8

from models_v2.base_model import *

logger = logging.getLogger('main')


@main_api_v2.route('/statistics_chatroom', methods = ['POST'])
def chatroom_statistics_chatroom():
    # verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)
    # date_type=1 今日实时，每10分钟计算一次，cache 10分钟
    # date_type=2 昨日，从daily取，cache10分钟
    # date_type3=7日，从daily计算过去7天，cache 10分钟
    # date_type=4 全部，从total表取，cache10分钟
    #   cache key=  dateType_clientId, cache value= {time():data}
    date_type = request.json.get('date_type', 1)
    run_hour = ''
    table = 'statistics_chatroom_hour'
    _timestamp = int(time.time())
    _where = []
    if (date_type == 1):
        run_hour = int(time.strftime('%H', time.localtime(time.time())))
        if (run_hour == 0):
            return make_response(SUCCESS)
        _where = ["and", ["<=", "run_hour", run_hour], ["=", "client_id", user_info.client_id]]
    elif (date_type == 2):
        day_diff = str(datetime.date.today() - datetime.timedelta(days = 1))
        time_arr = time.strptime(str(day_diff), "%Y-%m-%d")
        timestamp_diff = int(time.mktime(time_arr))
        _where = {"date": timestamp_diff, "client_id": user_info.client_id}
        # where = BaseModel.where_dict({"date":timestamp_diff,"client_id":user_info.client_id})
        table = 'statistics_chatroom_daily'
    elif (date_type == 3):
        day_diff = str(datetime.date.today() - datetime.timedelta(days = 7))
        time_arr = time.strptime(str(day_diff), "%Y-%m-%d")
        timestamp_diff = int(time.mktime(time_arr))
        table = 'statistics_chatroom_daily'

        _where = ["and", [">=", "date", timestamp_diff], ["=", "client_id", user_info.client_id]]
    elif (date_type == 4):
        table = 'statistics_chatroom_total'
        # where = BaseModel.where("=", "client_id", user_info.client_id)
        _where = {"client_id": user_info.client_id}

    cache_key = '_st' + str(date_type) + '_' + str(user_info.client_id)

    # group_id 群分组ID ， cache key =  dateType_clientId_groupId,
    # cache value= {time():data}  cache 10分钟
    group_id = request.json.get('group_id', '')
    if group_id:
        # 这里需要根据groupId 取 qunID list，或者前端post过来 qunID list
        group_id = ''

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
    # cacheData = 0
    if cacheData:
        print "cache hit"
        cacheData = json.loads(cacheData)
        for cd in cacheData:
            return make_response(SUCCESS, chatroom_list = cacheData[cd], last_update_time = cd)

    _where = BaseModel.where_dict(_where)

    print "------_where:::-----------\n", _where, order, "-----------------\n"

    chatroom_statis = BaseModel.fetch_all(table, '*', _where, page = 1, pagesize = pagesize, orderBy = order)
    chatroom_json_list = []

    chatroomnames = []
    for st in chatroom_statis:
        _stjson = st.to_json()
        chatroomnames.append(_stjson['chatroomname'])
        chatroom_json_list.append(_stjson)

    qunInfo = getQunInfo(chatroomnames)
    print "==========\n", qunInfo, "============\n"

    if (len(qunInfo) > 0):
        for ctlist in chatroom_json_list:
            if qunInfo.has_key(ctlist['chatroomname']):
                ctlist.update(qunInfo[ctlist['chatroomname']])
                print '9999999999', ctlist, '00000000000'

    last_update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_timestamp))

    if (len(chatroom_json_list) > 0):
        rds.set(cache_key, json.dumps({last_update_time: chatroom_json_list}))
        rds.expire(cache_key, 60 * 10)

    return make_response(SUCCESS, chatroom_list = chatroom_json_list, last_update_time = last_update_time)


# chatroomnames must array
def getQunInfo(chatroomnames):
    ret = {}
    if chatroomnames:
        qunInfo = BaseModel.fetch_all('a_chatroom', ['chatroomname', 'nickname', 'avatar_url'],
                                      BaseModel.where("in", "chatroomname", chatroomnames))
        if (qunInfo):
            for qf in qunInfo:
                _qfjson = qf.to_json()
                print '6666666666', _qfjson
                ret[_qfjson["chatroomname"]] = _qfjson
    return ret
