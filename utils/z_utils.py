# -*- coding: utf-8 -*-
"""
    Utils for ZYunH.
"""

from flask import request, jsonify
from functools import wraps


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


def response(body_as_dict):
    """Use make_response or not."""
    response_body = jsonify(body_as_dict)
    return response_body


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
