# -*- coding: utf-8 -*-

__version__ = "0.0.1"

import logging
from config import app

from utils import u_log

from api import login


@app.route('/hello')
def hello():
    return "hello"
    # return make_response(SUCCESS, str = "hello")


u_log.verify_logs_folder_exist()

logger = logging.getLogger('main')

if __name__ == '__main__':
    logger.debug("开始程序")
    app.run(host='0.0.0.0', port=4998, debug=True, use_reloader=False)
