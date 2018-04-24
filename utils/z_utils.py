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
