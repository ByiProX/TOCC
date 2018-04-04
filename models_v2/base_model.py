# -*- coding: utf-8 -*-
import copy
import json

from configs.config import DB_RULE


class BaseModel(object):
    def __init__(self, tablename = None, rules = None):
        self.__tablename = tablename
        self.__rules = rules
        self.__attrs = self.generate_attrs()

    def __repr__(self):
        return unicode(BaseModel.__module__) + u'.' + unicode(BaseModel.__name__) + u' instance at ' + unicode(hex(id(self)))

    def __getattr__(self, item):
        return self.__attrs[item]

    @staticmethod
    def create_model(tablename):
        base_model = BaseModel(tablename, DB_RULE[tablename])
        return base_model

    @staticmethod
    def extract_from_json():
        with open("../db_all.json", "r") as f:
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

    def save(self):
        # TODO: validate and save or update
        pass

    def load_from_json(self, data_json):
        # TODO: fill attr with json
        pass

    def fetch_all(self, select_colums, where_clause = None, limit = None, offset = None, order_by = None):
        query_clause = {"tablename": self.__tablename}
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
        # TODO query and init
        pass

    def fetch_one(self, select_colums, where_clause = None, order_by = None):
        query_clause = {"tablename": self.__tablename}
        if not select_colums == '*':
            if not isinstance(select_colums, list):
                select_colums = [select_colums]
            query_clause.update({"select": select_colums})

        if where_clause:
            query_clause.update(where_clause)
        if order_by:
            query_clause.update(order_by)
        query_clause.update({"limit": 1})
        # TODO query and initpass

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
    a_chatroom = CM("a_chatroom")
    print a_chatroom.chatroomname
    a_chatroom.chatroomname = '1'
    print a_chatroom.chatroomname
    pass
