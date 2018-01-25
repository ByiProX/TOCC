# -*- coding: utf-8 -*-
import json

from flask import request

from config import app
from core.login import verify_code


@app.route('/verify_code', methods=['POST'])
def app_verify_code():
    """
    用于验证
    code: 微信传入的code
    """
    data_json = json.loads(request.data)
    code = data_json.get('code')

    return verify_code(code)
