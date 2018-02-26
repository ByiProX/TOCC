# -*- coding: utf-8 -*-
# 开启gevent
from gevent import monkey, sleep

from maintenance.database_rel import create_all_databases
from maintenance.environment import environment_client_info

monkey.patch_all()

import logging

from configs.config import app, main_api, config_name_s
from core.production_core import production_thread

from utils import u_log
import models
import api
import configs

app.register_blueprint(main_api, url_prefix='/winner_api')

models.import_str = ""
api.api_str = ""
configs.config_str = ""

__version__ = "0.0.1a1"


@app.route('/hello')
def hello():
    return "hello"
    # return make_response(SUCCESS, str = "hello")


u_log.verify_logs_folder_exist()


def initial_all():
    create_all_databases()
    exit()


logger = logging.getLogger('main')
production_thread.start()

# 开启环境监测线程
if config_name_s == 'p':
    environment_client_info.start()

if __name__ == '__main__':
    logger.debug("开始程序")
    app.run(host='0.0.0.0', port=5500, debug=True, use_reloader=False)
