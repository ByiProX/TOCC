# -*- coding: utf-8 -*-

import logging
from config import app

from utils import u_log

import models
import api

models.import_str = ""
api.api_str = ""

__version__ = "0.0.2"


@app.route('/hello')
def hello():
    return "hello"
    # return make_response(SUCCESS, str = "hello")


u_log.verify_logs_folder_exist()


def initial_all():
    from maintenance import create_all_databases, initial_some_user_info, initial_some_bot_info
    create_all_databases()
    initial_some_user_info()
    initial_some_bot_info()
    exit()


logger = logging.getLogger('main')

if __name__ == '__main__':
    logger.debug("开始程序")
    app.run(host='0.0.0.0', port=4998, debug=True, use_reloader=False)
