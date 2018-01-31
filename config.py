# -*- coding: utf-8 -*-

import os

from flask import Flask, Blueprint
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

# print("---------------------------")
# print("-*       进入设置模式      *-")
# print("---------------------------")
#
# now_platform = str(platform())
# if now_platform == "Linux-2.6.18-412.el5-x86_64-with-redhat-5.11-Final":
#     res = raw_input("系统版本与235服务器相同，是否使用生产环境(y/n)? ")
#     if res == "y" or res == 'Y' or res == 'yes' or res == 'YES' or res == 'Yes':
#         config_name = 'production'
#     else:
#         print("目前使用平台:" + platform())
#         print("1 production")
#         print("2 dev")
#         print("3 test")
#         res = raw_input("请选择数据库版本，回车为dev版本(1/2/3)？")
#         if res == "1":
#             print("已选择production环境")
#             config_name = 'production'
#         elif res == "2" or res == "":
#             print("已选择dev环境")
#             config_name = 'dev'
#         elif res == "3":
#             print("已选择test环境")
#             config_name = 'test'
#         else:
#             raise ValueError("没有设置环境参数")
# else:
#     print("目前使用平台:" + platform())
#     print("1 production")
#     print("2 dev")
#     print("3 test")
#     res = raw_input("请选择数据库版本，回车为dev版本(1/2/3)？")
#     if res == "1":
#         print("该平台版本非服务器版本，请在服务器上运行或更新服务器版本")
#         config_name = 'dev'
#         exit()
#     elif res == "2" or res == "":
#         print("已选择dev环境")
#         config_name = 'dev'
#     elif res == "3":
#         print("已选择test环境")
#         config_name = 'test'
#     else:
#         raise ValueError("没有设置环境参数")
print("使用dev库")
config_name = 'dev'

app = Flask(__name__)
app.config.from_object(config_map[config_name])
config = config_map[config_name]
db = SQLAlchemy(app, session_options={"autoflush": False})

APP_ID = 'wxc8b40fcec9626528'
APP_SECRET = '6e63c26d856f7ecb1779f24ab2fc08f4'

main_api = Blueprint('api', __name__)

# 错误代码
ERROR_CODE = dict()
# 正常
SUCCESS = 'success'
ERROR_CODE[SUCCESS] = {'status_code': 0}
# 参数不合法
ERR_INVALID_PARAMS = 'err_invalid_params'
ERROR_CODE[ERR_INVALID_PARAMS] = {'discription': '参数不合法', 'status_code': -1}
# 用户token过期
ERR_USER_TOKEN_EXPIRED = 'err_user_token_expired'
ERROR_CODE[ERR_USER_TOKEN_EXPIRED] = {'discription': '用户token已过期', 'status_code': -2}
# 用户登录失败，没有得到有效token
ERR_USER_LOGIN_FAILED = 'err_user_login_failed'
ERROR_CODE[ERR_USER_LOGIN_FAILED] = {'discription': '用户登录失败，没有得到token', 'status_code': -3}
# 无效的token
ERR_USER_TOKEN = 'err_user_token'
ERROR_CODE[ERR_USER_TOKEN] = {'discription': '无效的token', 'status_code': -4}
# 操作内容与用户身份不符
ERR_WRONG_USER_ITEM = 'err_wrong_user_item'
ERROR_CODE[ERR_WRONG_USER_ITEM] = {'discription': '操作内容与用户身份不符', 'status_code': -5}
# 操作内容不存在或错误
ERR_WRONG_ITEM = 'err_wrong_item'
ERROR_CODE[ERR_WRONG_ITEM] = {'discription': '操作内容不存在或错误', 'status_code': -6}
# 设置参数错误
ERR_PARAM_SET = 'err_param_set'
ERROR_CODE[ERR_PARAM_SET] = {'discription': '设置参数错误', 'status_code': -7}
# 设置完成bot超过用户最大上限
ERR_MAXIMUM_BOT = 'err_maximum_bot'
ERROR_CODE[ERR_MAXIMUM_BOT] = {'discription': '设置完成bot超过用户最大上限', 'status_code': -8}
# 目前没有可用机器人
ERR_NO_ALIVE_BOT = 'err_no_alive_bot'
ERROR_CODE[ERR_NO_ALIVE_BOT] = {'discription': '目前没有可用机器人', 'status_code': -9}

# 建立默认分组时已有默认分组
WARN_HAS_DEFAULT_QUN = 'warn_has_default_qun'
ERROR_CODE[WARN_HAS_DEFAULT_QUN] = {'discription': '建立默认分组时已有默认分组', 'status_code': 1}

# 该用户目前无正在使用中的bot
INFO_NO_USED_BOT = 'info_no_used_bot'
ERROR_CODE[INFO_NO_USED_BOT] = {'discription': '该用户目前无正在使用中的bot', 'status_code': 20001}

# 用户的token过期时间（单位为日）
TOKEN_EXPIRED_THRESHOLD = 365
