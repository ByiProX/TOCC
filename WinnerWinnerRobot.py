# -*- coding: utf-8 -*-
# 开启gevent
from gevent import monkey, sleep

monkey.patch_all()

import logging

from configs.config import app, main_api
from core.consumption_core import consumption_thread
from core.production_core import production_thread
from maintenance import initial_a_bot

from utils import u_log
from maintenance import create_all_databases, initial_some_user_info, initial_some_bot_info, initial_user_bot_binded
import models
import api
import configs

app.register_blueprint(main_api, url_prefix='/api')

models.import_str = ""
api.api_str = ""
configs.config_str = ""

__version__ = "0.0.4a1"


@app.route('/hello')
def hello():
    return "hello"
    # return make_response(SUCCESS, str = "hello")


u_log.verify_logs_folder_exist()

def initial_all():
    create_all_databases()
    initial_some_user_info()
    initial_some_bot_info()
    initial_user_bot_binded()
    initial_a_bot()
    exit()


logger = logging.getLogger('main')
production_thread.start()
consumption_thread.start()

if __name__ == '__main__':
    logger.debug("开始程序")
    app.run(host='0.0.0.0', port=5500, debug=True, use_reloader=False)
