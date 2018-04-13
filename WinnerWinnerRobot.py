# -*- coding: utf-8 -*-
# 开启gevent
from gevent import monkey

from core.crawler_core import crawler_thread
from core_v2.message_core import start_listen_new_msg
from maintenance.database_rel import create_all_databases

import logging

from configs.config import app, main_api, main_api_v2
from core.production_core import production_thread
from models_v2.base_model import BaseModel

from utils import u_log
import models
import api
import api_v2
import configs

monkey.patch_all()
app.register_blueprint(main_api, url_prefix='/yaca_api')
app.register_blueprint(main_api_v2, url_prefix= '/yaca_api_v2')

models.import_str = ""
api.api_str = ""
api_v2.api_str = ""
configs.config_str = ""

__version__ = "0.0.1a1"


@app.route('/hello')
def hello():
    return "hello"
    # return make_response(SUCCESS, str = "hello")


@app.route('/yaca_api/hello')
def cia_api_hello():
    return "hello"
    # return make_response(SUCCESS, str = "hello")


u_log.verify_logs_folder_exist()


def initial_all():
    create_all_databases()
    exit()


logger = logging.getLogger('main')
# production_thread.start()
# crawler_thread.start()
start_listen_new_msg()
BaseModel.extract_from_json()

# 开启环境监测线程
# if config_name_s == 'p':
#     environment_client_info.start()

if __name__ == '__main__':
    logger.debug("开始程序")
    app.run(host='0.0.0.0', port=5505, debug=True, use_reloader=False)
