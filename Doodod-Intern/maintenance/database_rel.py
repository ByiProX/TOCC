# -*- coding: utf-8 -*-
from configs.config import db


def create_all_databases():
    """
    建立所有的数据库，而不删除库
    :return:
    """
    # if config_name == 'production':
    #     raise EnvironmentError("生产环境无法初始化库")
    # db.drop_all()
    db.create_all()
