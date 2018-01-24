# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ohayo'
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_POOL_SIZE = 100

    # app.config.setdefault('ERR_CODE', ERR_CODE)
    # app.config.setdefault('SUCCESS', SUCCESS)
    # app.config.setdefault('ERR_UNAUTH', ERR_UNAUTH)
    # app.config.setdefault('ERR_ALREADY_EXIST', ERR_ALREADY_EXIST)
    # app.config.setdefault('ERR_TOKEN_EXPIRED', ERR_TOKEN_EXPIRED)
    # app.config.setdefault('ERR_NONE_JSON', ERR_NONE_JSON)
    # app.config.setdefault('ERR_INVALID_PARAMS', ERR_INVALID_PARAMS)
    # app.config.setdefault('ERR_INVALID_USER', ERR_INVALID_USER)

    def __init__(self):
        pass


class ProductionConfig(Config):
    ABS_PATH = './assets'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
                              'mysql+pymysql://wechat:DOODOD.123456@101.251.222.236/cia'


config_map = {
    'production': ProductionConfig,

}

config_name = 'production'

app = Flask(__name__)
app.config.from_object(config_map[config_name])
config = config_map[config_name]

db = SQLAlchemy(app, session_options={"autoflush": False})

APP_ID = 'wxbe0f84cc2b873c72'
APP_SECRET = 'd6063862625c0a79719bc6167503f35e'

ERROR_CODE = dict()
SUCCESS = 'success'
ERROR_CODE[SUCCESS] = {'stats_code': 0}
ERR_INVALID_PARAMS = 'err_invalid_params'
ERROR_CODE[ERR_INVALID_PARAMS] = {'discription': '参数不合法', 'stats_code': -1}
