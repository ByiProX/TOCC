# -*- coding: utf-8 -*-

import logging
import threading
import time 
from copy import copy
 
from flask import request
from sqlalchemy import func

from core.send_task_and_ws_setting_core import check_chatroom_members_info
from core_v2.user_core import UserLogin
from models.android_db_models import AMember, AContact
from models.chatroom_member_models import MemberInfo, MemberOverview, MemberInviteMember, MemberAtMember, ChatroomInfo
from models.message_ext_models import MessageAnalysis
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from configs.config import SUCCESS, main_api_v2, db, rds, DEFAULT_PAGE, DEFAULT_PAGE_SIZE, ERR_INVALID_PARAMS, \
    ERR_INVALID_MEMBER, ERR_WRONG_ITEM
from utils.u_time import datetime_to_timestamp_utc_8

from models_v2.base_model import *

import datetime 
from urllib import urlencode,quote

logger = logging.getLogger('main')
 

def modelList2Arr(mlist):
    ret = []
    if mlist :
        for li in mlist:
            ret.append(li.to_json())
    return ret

  
#根据昵称搜索微信用户
def member_search(nickname): 
    print "\n\n\n ----  member_search ----------\n"
    _where = ["like","nickname", nickname.encode("utf-8")]
    _where = BaseModel.where_dict(_where)
    data = BaseModel.fetch_all('a_contact', '*' ,_where)
    data = modelList2Arr(data)
    print '==== ',_where,'== =======',data,'=== ===='
    print "\n ----  member_search end  ----------\n\n\n"
    return  data


#获取一个群里所有成员wxID
def getMembersOfQun(chatroomname): 
    print "\n\n\n ----  getMembersOfQun ----------\n"
    _where = ["=","chatroomname", chatroomname]
    _where = BaseModel.where_dict(_where)
    data = BaseModel.fetch_all('a_member', '*' ,_where)
    data = modelList2Arr(data)
    print '===========',_where,'===============',data,'=========='
    print "\n ----  getMembersOfQun  end  ----------\n\n\n"
    return  data
  
 

@main_api_v2.route('/statistics_member', methods = ['POST'])
def statistics_member():
    #verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)
    #date_type=1 今日实时，每10分钟计算一次，cache 10分钟
    #date_type=2 昨日，从daily取，cache10分钟  每晚上 0:10
    #date_type3=7日，从daily计算过去7天，cache 10分钟
    #date_type4=30日，从daily计算过去30天，cache 10分钟
    #date_type=5 全部，从total表取，cache10分钟
    #   cache key=  dateType_clientId, cache value= {time():data}
    date_type = request.json.get('date_type', 1)
    run_hour = ''
    table = 'statistics_member_hour'
    _timestamp = int(time.time())
    _dailyRunStamp = 0
    _where = []
    useranems = []
    cache_key = ''
    
    chatroomname = request.json.get('chatroomname' )
    if not chatroomname:
        return make_response(ERR_INVALID_PARAMS)
    else:
        #群ID，cache key = chatroomname ,cache 10分钟 
        _where ={"chatroomname":chatroomname}
        cache_key =  'st_'+chatroomname
    
    
    search_users = []
    nickname = request.json.get('keywords') 
    if nickname:
        print "\n ------ params:",nickname,chatroomname,"------\n"
        users_search = member_search(nickname)
        if users_search: 
            membersOfQun = getMembersOfQun(chatroomname)
            if membersOfQun:
                qmembers = json.loads(membersOfQun[0]['members'])
                for u in users_search:
                    for qm in qmembers:
                        if(u['username'] == qm['username']):
                            search_users.append(u)
                            useranems.append(u['username'])
    
    
    username = request.json.get('username')
    if username:
        useranems.append(username)

    print "\n ------ search_users :",search_users,"------\n"
    print "\n ------ useranems :",useranems,"------\n"

    if(date_type==1):
        run_hour = int( time.strftime('%H',time.localtime(time.time())))
        last_update_time = _timestamp - 600
        if(run_hour==0):
            return make_response(SUCCESS,member_list = [], last_update_time = last_update_time) 
        _where = ["and",["<=","run_hour",run_hour],["=","chatroomname",chatroomname],["in","username",useranems]] 
    elif(date_type==2):
        timestamp_diff = getTimeStamp(1)
        last_update_time =  timestamp_diff + 600  
        _where = ["and",["=","date",timestamp_diff],["=","chatroomname",chatroomname],["in","username",useranems]] 
        #where = BaseModel.where_dict({"date":timestamp_diff,"chatroomname":chatroomname})
        table = 'statistics_member_daily' 
    elif(date_type==3):
        timestamp_diff = getTimeStamp(7)
        last_update_time =  getTimeStamp(1) + 600 
        table = 'statistics_member_daily' 
        _where = ["and",[">=","date",timestamp_diff],["=","chatroomname",chatroomname],["in","username",useranems]] 
    elif(date_type==4):
        timestamp_diff = getTimeStamp(30)
        last_update_time =  getTimeStamp(1) + 600 
        table = 'statistics_member_daily' 
        _where = ["and",[">=","date",timestamp_diff],["=","chatroomname",chatroomname],["in","username",useranems]]  
    elif(date_type==5):
        table = 'statistics_member_total'
        last_update_time =  getTimeStamp(1) + 1200 
        #where = BaseModel.where("=", "chatroomname", chatroomname)
       # _where ={"chatroomname":chatroomname}
        _where = ["and",["=","chatroomname",chatroomname],["in","username",useranems]] 
    
    cache_key = cache_key +'_'+ str(date_type) 
 

    page = request.json.get('page',1)
    pagesize = request.json.get('pagesize', 30)
    cache_key = cache_key+'_p'+str(page)

    #规则是 active_count 是字段名，去掉count，变成 active_asc or active_desc
    order = request.json.get('order')
    if order:
        cache_key = cache_key+'_'+order
        order = order.split('_')
        order = order[0]+'_count'+' '+order[1]
    
    
    cacheData = rds.get(cache_key)
    cacheData = 0
    if cacheData:
        print "cache hit" 
        cacheData =  json.loads(cacheData)
        for cd in cacheData: 
            return make_response(SUCCESS, member_list = cacheData[cd], last_update_time = cd)
         
    
    print "\n ------_where value = -----------\n", _where,order ,"-----------------\n"
    _where = BaseModel.where_dict(_where)
    
    member_statis = BaseModel.fetch_all(table, '*' ,_where,page=1,pagesize=pagesize,orderBy=order)
    member_json_list = []
    
    print "\n ------member_statis = -----------\n", modelList2Arr(member_statis) ,"-----------------\n"

    if(len(member_statis)<=0):
        return make_response(SUCCESS,member_list=[],last_update_time=last_update_time)
 
    member_client_id = member_statis[0].client_id
   # memberfirst['client_id'] = 2
    if(member_client_id != user_info.client_id):
        return make_response(ERR_WRONG_ITEM)
    
    if len(useranems) > 0:
        wxIds = useranems
        userInfo = search_users
    else:
        wxIds = []
       
    for st in member_statis:
        _stjson = st.to_json()
        wxIds.append(_stjson['username'])
        member_json_list.append(_stjson)
    
    userInfo = getUserInfo(wxIds)
     
    print "\n========== userInfo = \n",userInfo,"============\n"
    

    if (len(userInfo)>0) :
        for ctlist in member_json_list:
            if userInfo.has_key(ctlist['username']):
                ctlist.update(userInfo[ctlist['username']])
                print '9999999999',ctlist,'00000000000'
    
    #last_update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(_timestamp))
    #last_update_time = _timestamp
    
    print "\n========== member_json_list = \n",member_json_list,"============\n"

    if(len(member_json_list)>0):
        rds.set(cache_key,json.dumps({last_update_time:member_json_list}))
        rds.expire(cache_key,10)

    return make_response(SUCCESS, member_list = member_json_list, last_update_time = last_update_time)





@main_api_v2.route('/statistics_memberone', methods = ['POST'])
def statistics_memberon():
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)
    username = request.json.get('username')
    if not username:
        return make_response(ERR_INVALID_PARAMS)
    userinfo =  BaseModel.fetch_one('a_contact', '*' ,BaseModel.where("=", "username", username))
    userinfo = userinfo.to_json()
    return make_response(SUCCESS,userinfo=userinfo)


#wxIds must array
def getUserInfo(wxIds):
    ret = {}
    if wxIds : 
        userInfo = BaseModel.fetch_all('a_contact', ['nickname','username','avatar_url'] ,BaseModel.where("in", "username", wxIds))
        if(userInfo):
            for qf in userInfo:
                _qfjson = qf.to_json()
                print '6666666666',_qfjson
                ret[_qfjson["username"]]= _qfjson 
    return ret
    

def getTimeStamp(d_diff=0):
    day_diff  = str(datetime.date.today() - datetime.timedelta(days=d_diff))
    time_arr = time.strptime(str(day_diff), "%Y-%m-%d")
    return int(time.mktime(time_arr))