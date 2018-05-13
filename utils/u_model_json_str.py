# -*- coding: utf-8 -*-

import logging
import json

from datetime import datetime
from flask import request
from flask import abort

logger = logging.getLogger('main')


def model_to_dict(inst, cls):
    """
    Jsonify the sqlalchemy query result. Skips attr starting with "_"
    """
    if inst is None:
        return {}
    # convert = {"DATETIME": datetime.isoformat}
    d = dict()
    for c in cls.__table__.columns:
        if c.name.startswith("_"):
            continue
        v = getattr(inst, c.name)
        current_type = str(c.type)
        if current_type == "DATETIME" and v is not None:
            try:
                d[c.name] = (v - datetime(1970, 1, 1, hour=8)).total_seconds() * 1000
            except:
                pass
                # d[c.name] = "Error:  Failed to covert using ", unicode(convert[c.type])
                d[c.name] = "Error: Failed to covert DATETIME"
        elif current_type.startswith('DECIMAL') and v is not None:
            d[c.name] = v.to_eng_string()
        elif v is None:
            d[c.name] = unicode()
        else:
            d[c.name] = v
    return d


def verify_json():
    logger.info(u"")
    logger.info(u"FromIP : " + request.remote_addr)
    logger.info(u"BaseUrl: " + request.base_url)
    logger.info(u"JsonArg: " + json.dumps(request.json))
    if request.json is None:
        abort(400)
        # return make_response(ERR_NONE_JSON)


def unicode_to_str(text):
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    return text


def model_to_dict(inst, cls):
    """
    Jsonify the sqlalchemy query result. Skips attr starting with "_"
    """
    if inst is None:
        return {}
    # convert = {"DATETIME": datetime.isoformat}
    d = dict()
    for c in cls.__table__.columns:
        if c.name.startswith("_"):
            continue
        v = getattr(inst, c.name)
        current_type = str(c.type)
        if current_type == "DATETIME" or current_type == "TIMESTAMP" and v is not None:
            try:
                d[c.name] = (v - datetime(1970, 1, 1, hour=8)).total_seconds() * 1000
            except:
                pass
                # d[c.name] = "Error:  Failed to covert using ", unicode(convert[c.type])
                d[c.name] = "Error: Failed to covert DATETIME"
        elif current_type.startswith('DECIMAL') and v is not None:
            d[c.name] = v.to_eng_string()
        elif v is None:
            d[c.name] = unicode()
        else:
            d[c.name] = v
    return d
