# -*- coding: utf-8 -*-
__author__ = 'Quentin'

import logging


# 定义MyLog类
class MyLogging(object):
    """
    此类用于创建一个自用的log
    默认的logging模块有6个级别。分别为：
    NOTSET    = 0
    DEBUG     = 10
    INFO      = 20
    WARNING   = 30
    ERROR     = 40
    CRITICAL  = 50
    """

    def __init__(self):
        user = 'wkx'
        # 第一步 创建一个logger
        self.logger = logging.getLogger(user)
        self.logger.setLevel(logging.INFO)  # log等级总开关

        # 第二步 创建一个handler，用于写入日志文件
        logfile = './logs/' + user + '.log'
        fh = logging.FileHandler(logfile, 'w+')
        fh.setLevel(logging.DEBUG)  # 只有DEBUG才被记录到file中

        # 第三步 再创建一个handler，用于输出到控制台console
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)  # 只有错误才被记录到console中

        # 第四步 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)-12s %(levelname)-8s %(name)-10s %(message)-12s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 第五步 将logger添加到handler里面
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    """日志的五个级别对应以下五个函数"""

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)


if __name__ == "__main__":
    myLog = MyLogging()
    myLog.debug("i am debug")
    myLog.info("i am info")
    myLog.warning("i am warning")
    myLog.error("i am error")
    myLog.critical("i am critical")
