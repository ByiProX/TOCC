# -*- coding: utf-8 -*-
import copy
import json
import logging
from urllib import urlencode

import requests
from datetime import datetime

from configs.config import DB_RULE, db, DB_SERVER_URL, SUCCESS, ERROR_CODE, UserBotR, BotInfo
from models.user_bot_models import UserInfo
from utils.u_model_json_str import model_to_dict
from utils.u_time import datetime_to_timestamp_utc_8

logger = logging.getLogger('main')


class BaseModel(object):
    def __init__(self, tablename = None, rules = None):
        self.__tablename = tablename
        self.__rules = rules
        self.attrs, self.__required = self.generate_attrs()

    def __repr__(self):
        return unicode(BaseModel.__module__) + u'.' + unicode(BaseModel.__name__) + u' instance at ' + unicode(hex(id(self)))

    @staticmethod
    def create_model(tablename):
        base_model = BaseModel(tablename, DB_RULE[tablename])
        return base_model

    @staticmethod
    def extract_from_json():
        with open("conf.json", "r") as f:
            DB_RULE.update(json.load(f))

    def get_tablename(self):
        return self.__tablename

    def get_rules(self):
        return self.__rules

    def generate_attrs(self):
        __attrs = list()
        __required = list()
        for rule in self.__rules:
            if rule[1] == "required":
                __required = rule[0]
                continue
            for attr in rule[0]:
                __attrs.append(attr)
                setattr(self, attr, None)
        return __attrs, __required

    def from_json(self, data_json):
        for key in data_json.keys():
            if key == u'_id' and data_json.get(key):
                _id = data_json.get(key)
                setattr(self, self.__tablename + u"_id", _id)
                # if isinstance(data_json.get(key), unicode) or isinstance(data_json.get(key), str):
                #     _id = data_json.get(key)
                # else:
                #     _id = data_json.get(key).get(u"$oid")
                # setattr(self, self.__tablename + u"_id", _id)
            if key in self.attrs:
                value = data_json.get(key)
                if isinstance(value, bool):
                    value = 1 if value else 0
                setattr(self, key, value)
        # if self._validate_all():
        #     return self
        # else:
        #     print u'validate failed'
        #     return None
        return self

    def to_json(self):
        # res_json = {__attr: __value for __attr, __value in self.attrs.iteritems()}
        # res_json = {attr: getattr(self, attr) for attr in self.attrs if getattr(self, attr) is not None}
        res_json = dict()
        for attr in self.attrs:
            if getattr(self, attr) is not None:
                value = getattr(self, attr)
                if isinstance(value, list) or isinstance(value, dict):
                    value = json.dumps(value)
                res_json[attr] = value
        return res_json

    def to_json_full(self):
        res_json = {attr: getattr(self, attr) for attr in self.attrs}
        return res_json

    def _validate_attr(self, __attr):
        if __attr not in self.attrs:
            return False
        __value = getattr(self, __attr)
        if __value is not None:
            for __rule in self.__rules:
                if __attr in __rule[0]:
                    __attr_type = __rule[1]
                    if __attr_type == u"required":
                        continue
                    if not BaseModel._call_validate(__attr_type, __value):
                        logger.error(u'type validate error: ' + unicode(__attr) + u' type: ' + unicode(type(__value)) + u' required type: ' + unicode(__attr_type))
                        return False
                    if len(__rule) > 2:
                        # print __rule[2]
                        for __rule_ext, __rule_params in __rule[2].iteritems():
                            if not BaseModel._call_validate(__rule_ext, __value, __rule_params):
                                logger.error(u'rule validate error: ' + unicode(__attr), u' value: ' + unicode(__value) + u' required rule: ' + unicode(__rule_ext) + u' ' + unicode(__rule_params))
                                return False
        return True

    def _validate_all(self):
        for __require in self.__required:
            if getattr(self, __require) is None:
                logger.error(u'require ' + unicode(__require))
                return False

        for __attr in self.attrs:
            if not self._validate_attr(__attr):
                return False
        return True

    @staticmethod
    def _call_validate(func_suffix, __value, __params = None):
        fun_validate = eval(u'BaseModel._validate_' + func_suffix)
        if callable(fun_validate):
            return fun_validate(__value, __params)

    @staticmethod
    def _validate_string(__value, __params = None):
        # print u'_validate_string'
        if isinstance(__value, str) or isinstance(__value, unicode):
            return True
        else:
            print __value, type(__value)
            return False

    @staticmethod
    def _validate_integer(__value, __params = None):
        # print u'_validate_integer'
        if isinstance(__value, int) or isinstance(__value, long):
            return True
        else:
            print __value, type(__value)
            return False

    @staticmethod
    def _validate_json(__value, __params = None):
        # print u'_validate_json'
        if isinstance(__value, dict) or isinstance(__value, list):
            return True
        else:
            print __value, type(__value)
            return False
        # try:
        #     json.loads(__value)
        #     return True
        # except:
        #     print __value, type(__value)
        #     return False

    @staticmethod
    def _validate_max(__value, __params = None):
        # print u'_validate_max'

        if __params is None:
            return False
        if len(__value) <= __params:
            return True
        else:
            print __value, __params, len(__value)
            return False

    def set_id(self, _id):
        setattr(self, self.__tablename + u"_id", _id)
        return self

    def get_id(self):
        if hasattr(self, self.__tablename + u'_id'):
            return getattr(self, self.__tablename + u'_id')
        else:
            return None

    def save(self):
        if not self._validate_all():
            logger.error(u"_validate failed")
            return False
        item_exist = None
        if self.__required:
            item_exist_where_clause = dict()
            for __require in self.__required:
                value = getattr(self, __require)
                item_exist_where_clause.setdefault(__require, value)
            item_exist = BaseModel.fetch_one(self.__tablename, '*', where_clause = {"where": json.dumps(item_exist_where_clause)})
        self_id = self.get_id()
        if self_id is None and item_exist is None:
            # 插入
            return self.db_post()
        else:
            # 更新
            if self_id is None:
                self.set_id(item_exist.get_id())
            return self.db_put()
        # return self

    def update(self):
        if not self._validate_all():
            logger.error(u"_validate failed")
            return False
        return self.db_put()
        # return self

    def delete(self):
        if self.__tablename not in ["client_group_r", "wallet", "keywords"]:
            return False
        return self.db_delete()

    # 保存
    def db_post(self):
        url = DB_SERVER_URL + self.__tablename + u's'
        data = self.to_json()
        response = requests.post(url = url, data = data)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        # load _id
        if code == 0:
            msg = response_json.get(u"data").get(u"id")
            self.set_id(msg)
            return True
        else:
            logger.error(u"insert failed, content: " + unicode(response.content))
            logger.error(u"insert failed, self.json: " + json.dumps(self.to_json_full()))
            return False
        # return self

    # 更新
    def db_put(self):
        _id = self.get_id()
        if _id is None:
            logger.error(u"update failed, _id is None")
            return False
        url = DB_SERVER_URL + self.__tablename + u'/' + unicode(_id)
        data = self.to_json()
        response = requests.put(url = url, data = data)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        if code == 0:
            msg = response_json.get(u"data").get(u"id")
            self.set_id(msg)
            return True
        else:
            logger.error(u"update failed, content: " + unicode(response.content))
            logger.error(u"update failed, self.json: " + json.dumps(self.to_json_full()))
            return False
        # return self

    # 删除
    def db_delete(self):
        _id = self.get_id()
        if _id is None:
            logger.error(u"delete failed, _id is None")
            return False
        url = DB_SERVER_URL + self.__tablename + u'/' + unicode(_id)
        data = self.to_json()
        response = requests.delete(url = url, data = data)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        if code == 0:
            msg = response_json.get(u"msg")
            self.set_id(msg)
            return True
        else:
            logger.error(u"update failed, content: " + unicode(response.content))
            return False

    @staticmethod
    def count(tablename, where_clause = None, **kwargs):
        query_clause = dict()
        query_clause.update({"count": 1})
        if where_clause:
            query_clause.update(where_clause)
        query_clause.update(kwargs)
        url = DB_SERVER_URL + tablename + u's'
        response = requests.get(url = url, params = query_clause)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        count = 0
        if code == 0 and response.status_code == 200:
            count = response_json.get(u"count")
        else:
            logger.error(u"query failed, content: " + unicode(response.content))
        return count

    @staticmethod
    def fetch_all(tablename, select_colums, where_clause = None, limit = None, offset = None, order_by = None, page = None, pagesize = None, group = None, **kwargs):
        query_clause = dict()
        total_flag = True
        if not select_colums == '*':
            if not isinstance(select_colums, list):
                select_colums = [select_colums]
            query_clause.update({"select": json.dumps(select_colums)})
        if where_clause:
            query_clause.update(where_clause)
        if limit:
            query_clause.update(limit)
            total_flag = False
        if offset:
            query_clause.update(offset)
            total_flag = False
        if order_by:
            query_clause.update(order_by)
            total_flag = False
        if page:
            query_clause.update({"page": page})
            total_flag = False
        if page:
            query_clause.update({"pageSize": pagesize})
            total_flag = False
        if group:
            query_clause.update({"group": group})

        query_clause.update(kwargs)
        query_clause.setdefault("pageSize", 100)
        query_clause.setdefault("page", 1)

        item_list = list()
        url = DB_SERVER_URL + tablename + u's'
        # logger.info(u"request url : " + url)
        # if query_clause:
        #     url += u"?"
        #     for key, value in query_clause.iteritems():
        #         url += unicode(key) + u"=" + urlencode(unicode(value)) + u"&"
        page = 1
        errTry = 1 
        eof = False
        while not eof:
            if errTry>=3:
                eof = True
                return item_list
            response = requests.get(url = url, params = query_clause)
            # print response.request.url
            page += 1
            query_clause["page"] = page
            # if group:
            #     print response.request.url
            # print response.request.url
            if response.status_code == 200:
                response_json = json.loads(response.content)
                code = response_json.get(u"code")
                if code == 0:
                    data = response_json.get(u"data")
                    for item in data:
                        item_list.append(CM(tablename).from_json(item))
                    pages = response_json.get(u"pages")
                    if pages and response_json.get(u"pages").get(u"pageCount"):
                        page_count = response_json.get(u"pages").get(u"pageCount")
                        if page > page_count:
                            eof = True
                    else:
                        eof = True
                else:
                    errTry += 1
                    logger.error(u"query failed, content: " + unicode(response.content))
            else:
                errTry += 1
                logger.error(u"query failed, content: " + unicode(response.content))

            if not total_flag:
                break
        return item_list

    @staticmethod
    def fetch_one(tablename, select_colums, where_clause = None, order_by = None, **kwargs):
        query_clause = dict()
        if not select_colums == '*':
            if not isinstance(select_colums, list):
                select_colums = [select_colums]
            query_clause.update({"select": select_colums})

        if where_clause:
            query_clause.update(where_clause)
        if order_by:
            query_clause.update(order_by)
        query_clause.update({"limit": 1})

        query_clause.update(kwargs)

        item = None
        url = DB_SERVER_URL + tablename + u's'
        # if query_clause:
        #     url += u"?"
        #     for key, value in query_clause.iteritems():
        #         url += unicode(key) + u"=" + urlencode(unicode(value)) + u"&"
        response = requests.get(url = url, params = query_clause)
        if response.status_code == 200:
            response_json = json.loads(response.content)
            code = response_json.get(u"code")
            if code == 0:
                data = response_json.get(u"data")
                if data:
                    item = CM(tablename).from_json(data[0])
            else:
                logger.error(u"query failed, content: " + unicode(response.content))
        else:
            logger.error(u"query failed, content: " + unicode(response.content))
        return item

    @staticmethod
    def fetch_by_id(tablename, _id):
        url = DB_SERVER_URL + tablename + u'/' + unicode(_id)
        item = None
        response = requests.get(url = url)
        if response.status_code == 200:
            response_json = json.loads(response.content)
            code = response_json.get(u"code")
            if code == 0:
                data = response_json.get(u"data")
                if data:
                    item = CM(tablename).from_json(data)
            else:
                logger.error(u"query failed, content: " + unicode(response.content))
        else:
            logger.error(u"query failed, content: " + unicode(response.content))
        return item

    @staticmethod
    def where_dict(where_dict):
        where_clause = {"where": json.dumps(where_dict)}
        return where_clause

    @staticmethod
    def limit(limit):
        limit_clause = {"limit": limit}
        return limit_clause

    @staticmethod
    def offset(offset):
        offset_clause = {"offset": offset}
        return offset_clause

    @staticmethod
    def order_by(order_dict):
        order_str = unicode()
        for key, value in order_dict.iteritems():
            if order_str != u"":
                order_str += u", "
            order_str += key + u" " + value
        order_clause = {"orderBy": order_str}
        return order_clause

    @staticmethod
    def where(operator, key, value):
        where_clause_list = list()
        where_clause_list.append(operator)
        where_clause_list.append(key)
        where_clause_list.append(value)
        where_clause = {"where": json.dumps(where_clause_list)}
        return where_clause

    # @staticmethod
    # def and_(where_clause1, where_clause2):
    #     where_clause_list = list()
    #     where_clause_list.append('and')
    #     where_clause_list.append(where_clause1)
    #     where_clause_list.append(where_clause2)
    #     where_clause = {"where": json.dumps(where_clause_list)}
    #     return where_clause

    # 这样好用一点，请组织审查，建议'or_'同样修改
    @staticmethod
    def and_(*where_clauses):
        where_clause_list = list()
        where_clause_list.append('and')
        for where_clause in where_clauses:
            where_clause_list.append(where_clause)
        where_clause = {"where": json.dumps(where_clause_list)}
        return where_clause

    @staticmethod
    def or_(*where_clauses):
        where_clause_list = list()
        where_clause_list.append('or')
        for where_clause in where_clauses:
            where_clause_list.append(where_clause)
        where_clause = {"where": where_clause_list}
        return where_clause


CM = BaseModel.create_model


def extract_from_json():
    with open("conf.json", "r") as f:
        DB_RULE.update(json.load(f))


extract_from_json()


if __name__ == '__main__':
    BaseModel.extract_from_json()
    now_time = datetime_to_timestamp_utc_8(datetime.now())
    client = BaseModel.fetch_by_id(u"client", 1)
    client.client_id = int(client.client_id)
    client.create_time = long(client.create_time)
    client.update_time = long(client.update_time)
    # client.client_name = u"Doodod"
    # client.client_cn_name = u"独到科技"
    # client.tel = u"18888888888"
    # client.admin = u"neil"
    # client.update_time = datetime_to_timestamp_utc_8(datetime.now())
    # client.save()
    # user_list = db.session.query(UserInfo).all()
    user_old = db.session.query(UserInfo).filter(UserInfo.user_id == 5).first()
    user_old_json = model_to_dict(user_old, user_old.__class__)
    user_old_json['client_id'] = client.client_id
    user_old_json['last_login_time'] = int(user_old_json['last_login_time']) / 1000
    user_old_json['token_expired_time'] = int(user_old_json['token_expired_time']) / 1000
    user_old_json['create_time'] = int(user_old_json['create_time']) / 1000
    user = CM("client_member").from_json(user_old_json)
    user_switch = CM('client_switch').from_json(user_old_json)
    user.code = "111"
    user.token = "222"
    user.save()
    user_switch.save()

    bot_info = CM(BotInfo)
    bot_info.username = u"wxid_3mxn6zyskbpt22"
    bot_info.create_bot_time = now_time
    bot_info.is_alive = 1
    bot_info.alive_detect_time = now_time
    bot_info.save()

    ubr = CM(UserBotR)
    ubr.client_id = client.client_id
    ubr.bot_username = bot_info.username
    ubr.chatbot_default_nickname = u"奔跑的小黄豆"
    ubr.is_work = 1
    ubr.create_time = now_time
    ubr.save()
    # for user in user_list:
    #     client = CM('client')
    #     client.create_time = datetime_to_timestamp_utc_8(datetime.now())
    #     client.client_name = user.open_id
    #     client.admin = user.open_id
    #     client.save()
    #     user_json = model_to_dict(user, user.__class__)
    #     user_json['client_id'] = client.client_id
    #     user_json['open_id'] += "a"
    #     user_json['last_login_time'] = int(user_json['last_login_time']) / 1000
    #     user_json['token_expired_time'] = int(user_json['token_expired_time']) / 1000
    #     user_json['create_time'] = int(user_json['create_time']) / 1000
    #     user_info = CM('client_member').from_json(user_json)
    #     user_switch = CM('client_switch').from_json(user_json)
    #     user_info.save()
    #     user_switch.save()
    # user_info_list = BaseModel.fetch_all('client_member', "*", order_by = BaseModel.order_by({"union_id": "desc"}))
    # user_info = BaseModel.fetch_by_id(u'client_member', u'5acb919f421aa9393f212b88')
    # user_info.union_id = "1"
    # user_info.update()
    pass
