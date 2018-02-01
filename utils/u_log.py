# -*- coding: utf-8 -*-

import os
import logging
from logging import config

logger = logging.getLogger('main')


def verify_logs_folder_exist():
    logger.debug("检查logs目录是否存在")
    if os.path.exists('./logs') is False:
        logger.warning("没有找到logs目录,将新建目录")
        os.mkdir('./logs')
    else:
        pass
    logging.config.fileConfig('./configs/logging.conf')
    logger.debug('logs目录检查完毕 - OK')
