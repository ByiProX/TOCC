# -*- coding: utf-8 -*-
import os
from configs.config import config_name_s
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
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or 'mysql+pymysql://wechat:DOODOD.123456@101.251.222.236/WinnerWinnerRobot'
    SQLALCHEMY_BINDS = {'android_db': 'mysql+pymysql://wechat:DOODOD.123456@101.251.222.236/cia'}


class DevelopmentConfig(Config):
    ABS_PATH = './assets'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or 'mysql+pymysql://wechat:DOODOD.123456@101.251.222.236/DevWinnerWinnerRobot'
    SQLALCHEMY_BINDS = {'android_db': 'mysql+pymysql://wechat:DOODOD.123456@101.251.222.236/cia'}


class TestConfig(Config):
    ABS_PATH = './assets'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or 'mysql+pymysql://wechat:DOODOD.123456@101.251.222.236/TestWinnerWinnerRobot'
    SQLALCHEMY_BINDS = {'android_db': 'mysql+pymysql://wechat:DOODOD.123456@101.251.222.236/cia'}


config_map = {
    'production': ProductionConfig,
    'dev': DevelopmentConfig,
    'test': TestConfig,
}
config_name_s = config_name_s

if config_name_s == 'p':
    print("注意！线上环境！使用production库")
    config_name = 'production'
elif config_name_s == 'd':
    print("使用dev库")
    config_name = 'dev'
elif config_name_s == 't':
    print("使用test库")
    config_name = 'test'
else:
    raise ValueError

test_app = Flask(__name__)
test_app.config.from_object(config_map[config_name])
test_db = SQLAlchemy(test_app, session_options={"autoflush": False})
