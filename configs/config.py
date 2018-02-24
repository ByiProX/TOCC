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


class WenFaDevelopmentConfig(Config):
    ABS_PATH = './assets'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or 'mysql+pymysql://winner_robot:winnerwinnerrobot0134@127.0.0.1/DevWinnerWinnerRobot'
    SQLALCHEMY_BINDS = {'android_db': 'mysql+pymysql://winner_robot:winnerwinnerrobot0134@127.0.0.1/cia'}


config_map = {
    'production': ProductionConfig,
    'dev': DevelopmentConfig,
    'test': TestConfig,
    'zwf_dev': WenFaDevelopmentConfig
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
config_name_s = 'd'

if config_name_s == 'p':
    print("注意！线上环境！使用production库")
    config_name = 'production'
elif config_name_s == 'd':
    print("使用dev库")
    config_name = 'dev'
elif config_name_s == 't':
    print("使用test库")
    config_name = 'test'
elif config_name_s == 'z':
    print("使用文法的本地环境进行测试")
    config_name = 'zwf_dev'
else:
    raise ValueError

app = Flask(__name__)
app.config.from_object(config_map[config_name])
config = config_map[config_name]
db = SQLAlchemy(app, session_options={"autoflush": False})

APP_ID = 'wxc8b40fcec9626528'
APP_SECRET = '6e63c26d856f7ecb1779f24ab2fc08f4'

main_api = Blueprint('api', __name__)

# 生成所有任务的循环和发送所有任务的循环所需要用的时间
PRODUCTION_CIRCLE_INTERVAL = 1
CONSUMPTION_CIRCLE_INTERVAL = 1

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
# 无法获得该bot的二维码
ERR_NO_BOT_QR_CODE = 'err_no_bot_qr_code'
ERROR_CODE[ERR_NO_BOT_QR_CODE] = {'discription': '无法获得该bot的二维码', 'status_code': -10}
# 找到多名符合名称的人，无法确定是谁加了bot好友
ERR_HAVE_SAME_PEOPLE = 'err_have_same_people'
ERROR_CODE[ERR_HAVE_SAME_PEOPLE] = {'discription': '找到多名符合名称的人，无法确定是谁加了bot好友', 'status_code': -10}
# 遇到未知或不可能错误
ERR_UNKNOWN_ERROR = 'err_unknown_error'
ERROR_CODE[ERR_UNKNOWN_ERROR] = {'discription': '遇到未知或不可能错误', 'status_code': -11}
# 未分组不能进行重命名或删除
ERR_RENAME_OR_DELETE_DEFAULT_GROUP = 'err_rename_or_delete_default_group'
ERROR_CODE[ERR_RENAME_OR_DELETE_DEFAULT_GROUP] = {'discription': '未分组不能进行重命名或删除', 'status_code': -12}
# 循环状态不对，无法改变
ERR_CIRCLE_STATUS_WRONG = 'err_circle_status_wrong'
ERROR_CODE[ERR_RENAME_OR_DELETE_DEFAULT_GROUP] = {'discription': '循环状态不对，无法改变', 'status_code': -13}
# 设置内容的长度不符
ERR_SET_LENGTH_WRONG = 'err_set_length_wrong'
ERROR_CODE[ERR_SET_LENGTH_WRONG] = {'discription': '设置内容的长度不符', 'status_code': -14}
# 功能未开启，无法使用
ERR_WRONG_FUNC_STATUS = 'err_wrong_func_status'
ERROR_CODE[ERR_WRONG_FUNC_STATUS] = {'discription': '功能未开启，无法使用', 'status_code': -15}

# 建立默认分组时已有默认分组
WARN_HAS_DEFAULT_QUN = 'warn_has_default_qun'
ERROR_CODE[WARN_HAS_DEFAULT_QUN] = {'discription': '建立默认分组时已有默认分组', 'status_code': 1}

# 遇到被try到的未知错误
CRITICAL_HAS_EXCEPT = 'critical_has_except'
ERROR_CODE[CRITICAL_HAS_EXCEPT] = {'discription': '遇到被try到的未知错误', 'status_code': -1001}

# 该用户目前无正在使用中的bot
INFO_NO_USED_BOT = 'info_no_used_bot'
ERROR_CODE[INFO_NO_USED_BOT] = {'discription': '该用户目前无正在使用中的bot', 'status_code': 20001}

# 用户的token过期时间（单位为日）
TOKEN_EXPIRED_THRESHOLD = 365

# consumption类型
CONSUMPTION_TASK_TYPE = {"batch_sending_task": 1, "auto_reply": 2, "daily_bonus": 3, "welcome_message": 4}

# 发送内容的类型；1为文字；2为图片；3为链接；4为文件；5为小程序；6为公众号；7为视频；8为语音
TASK_SEND_TYPE = {
    "text": 1,
    "picture": 2,
    "link": 3,
    "file": 4,
    "mini_programs": 5,
    "massive_platform": 6,
    "video": 7,
    "voice": 8
}

# 全局匹配规则更新标记，每次更新规则库需将锁打开
GLOBAL_MATCHING_RULES_UPDATE_FLAG = dict()
GLOBAL_MATCHING_RULES_UPDATE_FLAG.setdefault("global_matching_rules_update_flag", True)

MSG_TYPE_UNKNOWN = -1  # 未知类型
MSG_TYPE_TXT = 1
MSG_TYPE_PIC = 3
MSG_TYPE_MP3 = 34
MSG_TYPE_NAME_CARD = 42
MSG_TYPE_MP4 = 43
MSG_TYPE_GIF = 47
MSG_TYPE_VIDEO = 62
MSG_TYPE_SHARE = 49
MSG_TYPE_SYS = 10000

WS_MAP = dict()
