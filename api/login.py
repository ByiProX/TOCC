# -*- coding: utf-8 -*-
from config import app
from core.login import verify_code


@app.route('/verify_code', methods=['POST'])
def app_verify_code():
    return verify_code()
