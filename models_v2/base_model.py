# -*- coding: utf-8 -*-
import copy
import json
import logging
from urllib import urlencode

import requests

from configs.config import DB_RULE, db, SECRET_ATTR_SET, DB_SERVER_URL, SUCCESS, ERROR_CODE
from models.user_bot_models import UserInfo
from utils.u_model_json_str import model_to_dict

logger = logging.getLogger('main')


class BaseModel(object):
    def __init__(self, tablename = None, rules = None):
        self.__tablename = tablename
        self.__rules = rules
        self.__attrs = self.generate_attrs()

    def __repr__(self):
        return unicode(BaseModel.__module__) + u'.' + unicode(BaseModel.__name__) + u' instance at ' + unicode(hex(id(self)))

    def __getattr__(self, item):
        return self.__attrs[item]

    # def __setattr__(self, key, value):
    #     if key in
    #     return self.__attrs.setdefault(key, value)

    @staticmethod
    def create_model(tablename):
        base_model = BaseModel(tablename, DB_RULE[tablename])
        return base_model

    @staticmethod
    def extract_from_json():
        with open("../conf.json", "r") as f:
            DB_RULE.update(json.load(f))

    def get_tablename(self):
        return self.__tablename

    def get_rules(self):
        return self.__rules

    def generate_attrs(self):
        __attrs = dict()
        for rule in self.__rules:
            for attr in rule[0]:
                __attrs.setdefault(attr, None)
        return __attrs

    def from_json(self, data_json):
        for key in data_json.keys():
            if key == u'_id':
                _id = data_json.get(key).get(u"$oid")
                self.__attrs.setdefault(self.__tablename + u"_id", _id)
            if key in self.__attrs.keys():
                value = data_json.get(key)
                if isinstance(value, bool):
                    value = 1 if value else 0
                self.__attrs[key] = value
        # if self._validate_all():
        #     return self
        # else:
        #     print u'validate failed'
        #     return None
        return self

    def to_json(self):
        res_json = {__attr: __value for __attr, __value in self.__attrs.iteritems() if __attr not in SECRET_ATTR_SET}
        return res_json

    def _validate_attr(self, __attr):
        if __attr not in self.__attrs.keys():
            return False
        __value = getattr(self, __attr)
        if __value is not None:
            for __rule in self.__rules[1:]:
                if __attr in __rule[0]:
                    __attr_type = __rule[1]
                    if not BaseModel._call_validate(__attr_type, __value):
                        logger.error(u'type validate error: ' + unicode(__attr) + u' type: ' + unicode(type(__value)) + u' required type: ' + unicode(__attr_type))
                        return False
                    if len(__rule) > 2:
                        print __rule[2]
                        for __rule_ext, __rule_params in __rule[2].iteritems():
                            if not BaseModel._call_validate(__rule_ext, __value, __rule_params):
                                logger.error(u'rule validate error: ' + unicode(__attr), u' value: ' + unicode(__value) + u' required rule: ' + unicode(__rule_ext) + u' ' + unicode(__rule_params))
                                return False
        return True

    def _validate_all(self):
        __requires = self.__rules[0][0]
        for __require in __requires:
            if getattr(self, __require) is None:
                logger.error(u'require ' + unicode(__require))
                return False

        for __attr in self.__attrs.keys():
            self._validate_attr(__attr)
        return True

    @staticmethod
    def _call_validate(func_suffix, __value, __params = None):
        fun_validate = eval(u'BaseModel._validate_' + func_suffix)
        if callable(fun_validate):
            return fun_validate(__value, __params)

    @staticmethod
    def _validate_string(__value, __params = None):
        print u'_validate_string'
        if isinstance(__value, str) or isinstance(__value, unicode):
            return True
        else:
            return False

    @staticmethod
    def _validate_integer(__value, __params = None):
        print u'_validate_integer'
        if isinstance(__value, int) or isinstance(__value, long):
            return True
        else:
            return False

    @staticmethod
    def _validate_json(__value, __params = None):
        print u'_validate_json'
        try:
            json.loads(__value)
            return True
        except:
            return False

    @staticmethod
    def _validate_max(__value, __params = None):
        print u'_validate_max'

        if __params is None:
            return False
        print __value, __params, len(__value)
        if len(__value) <= __params:
            return True
        else:
            return False

    def set_id(self, _id):
        self.__attrs[self.__tablename + u"_id"] = _id
        return self

    def get_id(self):
        return self.__attrs.get(self.__tablename + u'_id')

    def save(self):
        if not self._validate_all():
            logger.error(u"_validate failed")
            return
        item_exist_where_clause = dict()
        for __require in self.__rules[0][0]:
            value = getattr(self, __require)
            item_exist_where_clause.setdefault(__require, value)
        item_exist = BaseModel.fetch_one(self.__tablename, '*', where_clause = item_exist_where_clause)
        if self.get_id() is not None or item_exist is not None:
            # 插入
            self.db_post()
        else:
            # 更新
            self.db_put()
        return self

    # TODO: validate and update
    def update(self):
        if not self._validate_all():
            logger.error(u"_validate failed")
            return
        self.db_put()
        return self

    # 保存
    def db_post(self):
        url = DB_SERVER_URL + self.__tablename + u's'
        data = self.to_json()
        response = requests.post(url = url, data = data)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        # load _id
        if code == 0:
            msg = response_json.get(u"msg")
            self.set_id(_id = msg)
        else:
            logger.error(u"insert failed, content: " + unicode(response.content))
        return self

    # 更新
    def db_put(self):
        _id = self.get_id()
        if _id is None:
            logger.error(u"update failed, _id is None")
            return self
        url = DB_SERVER_URL + self.__tablename + u'/' + _id
        data = self.to_json()
        response = requests.put(url = url, data = data)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        if code == 0:
            msg = response_json.get(u"msg")
            self.set_id(_id = msg)
        else:
            logger.error(u"update failed, content: " + unicode(response.content))
        return self

    @staticmethod
    def fetch_all(tablename, select_colums, where_clause = None, limit = None, offset = None, order_by = None):
        query_clause = dict()
        if not select_colums == '*':
            if not isinstance(select_colums, list):
                select_colums = [select_colums]
            query_clause.update({"select": select_colums})
        if where_clause:
            query_clause.update(where_clause)
        if limit:
            query_clause.update(limit)
        if offset:
            query_clause.update(offset)
        if order_by:
            query_clause.update(order_by)

        item_list = list()
        url = DB_SERVER_URL + tablename + u's'
        # if query_clause:
        #     url += u"?"
        #     for key, value in query_clause.iteritems():
        #         url += unicode(key) + u"=" + urlencode(unicode(value)) + u"&"
        response = requests.get(url = url, params = query_clause)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        if code == 0:
            data = response_json.get(u"data")
            for item in data:
                item_list.append(CM(tablename).from_json(item))
        else:
            logger.error(u"query failed, content: " + unicode(response.content))
        return item_list

    @staticmethod
    def fetch_one(tablename, select_colums, where_clause = None, order_by = None):
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

        item = None
        url = DB_SERVER_URL + tablename + u's'
        # if query_clause:
        #     url += u"?"
        #     for key, value in query_clause.iteritems():
        #         url += unicode(key) + u"=" + urlencode(unicode(value)) + u"&"
        response = requests.get(url = url, params = query_clause)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        if code == 0:
            data = response_json.get(u"data")
            if data:
                item = CM(tablename).from_json(data[0])
        else:
            logger.error(u"query failed, content: " + unicode(response.content))
        return item

    @staticmethod
    def fetch_by_id(tablename, _id):
        url = DB_SERVER_URL + tablename + u'/' + _id
        item = None
        response = requests.get(url = url)
        response_json = json.loads(response.content)
        code = response_json.get(u"code")
        if code == 0:
            data = response_json.get(u"data")
            if data:
                item = CM(tablename).from_json(data)
        else:
            logger.error(u"query failed, content: " + unicode(response.content))
        return item

    @staticmethod
    def where_dict(where_dict):
        where_clause = {"where": where_dict}
        return where_clause

    @staticmethod
    def limit(limit):
        limit_clause = {"limit", limit}
        return limit_clause

    @staticmethod
    def offset(offset):
        offset_clause = {"offset": offset}
        return offset_clause

    @staticmethod
    def order_by(order_dict):
        order_str = unicode()
        for key, value in order_dict:
            if order_str != u"":
                order_str += u", "
            order_str += key + u" " + value
        order_clause = {"order_by": order_str}
        return order_clause

    @staticmethod
    def where(operator, key, value):
        where_clause_list = list()
        where_clause_list.append(operator)
        where_clause_list.append(key)
        where_clause_list.append(value)
        where_clause = {"where": where_clause_list}
        return where_clause

    @staticmethod
    def and_(where_clause1, where_clause2):
        where_clause_list = list()
        where_clause_list.append('and')
        where_clause_list.append(where_clause1)
        where_clause_list.append(where_clause2)
        where_clause = {"where": where_clause_list}
        return where_clause

    @staticmethod
    def or_(where_clause1, where_clause2):
        where_clause_list = list()
        where_clause_list.append('or')
        where_clause_list.append(where_clause1)
        where_clause_list.append(where_clause2)
        where_clause = {"where": where_clause_list}
        return where_clause


CM = BaseModel.create_model

if __name__ == '__main__':
    BaseModel.extract_from_json()
    user = db.session.query(UserInfo).first()
    user_json = model_to_dict(user, user.__class__)
    user_json['client_id'] = 1
    user_json['last_login_time'] = int(user_json['last_login_time']) / 1000
    user_json['token_expired_time'] = int(user_json['token_expired_time']) / 1000
    user_json['create_time'] = int(user_json['create_time']) / 1000
    user_info = CM('client_member').from_json(user_json)
    user_info.save()
    # user_info_list = BaseModel.fetch_all('client_member', '*')
    # user_info = BaseModel.fetch_by_id(u'client_member', u'5aca233d421aa939413cc042')
    pass
