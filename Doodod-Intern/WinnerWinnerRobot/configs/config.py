# -*- coding: utf-8 -*-

import os
from Queue import Queue

import redis
from decimal import Decimal

from flask import Flask, Blueprint, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import Headers
# from Crypto import Random
# from Crypto.PublicKey import RSA
# from Crypto.Cipher import PKCS1_v1_5
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider

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


ENV = 'DEV'
if os.path.exists("online_config"):
    ENV = 'PRODUCTION'

class ProductionConfig(Config):
    ABS_PATH = './assets'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or 'mysql+pymysql://back_end_spe:IyhSnnYAng6dCjD9@101.251.222.236/YACA'
    SQLALCHEMY_BINDS = {'android_db': 'mysql+pymysql://back_end_spe:IyhSnnYAng6dCjD9@101.251.222.236/cia'}


class DevelopmentConfig(Config):
    ABS_PATH = './assets'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or 'mysql+pymysql://back_end_spe:IyhSnnYAng6dCjD9@101.251.222.236/YACADev'
    SQLALCHEMY_BINDS = {'android_db': 'mysql+pymysql://back_end_spe:IyhSnnYAng6dCjD9@101.251.222.236/cia'}


class TestConfig(Config):
    ABS_PATH = './assets'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI') or 'mysql+pymysql://back_end_spe:IyhSnnYAng6dCjD9@101.251.222.236/YACATest'
    SQLALCHEMY_BINDS = {'android_db': 'mysql+pymysql://back_end_spe:IyhSnnYAng6dCjD9@101.251.222.236/cia'}

class MyResponse(Response):
    """解决跨域问题"""
    def __init__(self, response=None, **kwargs):
        kwargs['headers'] = ''
        headers = kwargs.get('headers')
        origin = ('Access-Control-Allow-Origin', '*')
        # origin_1 = ('Access-Control-Allow-Origin', 'http://xuanren360.com')
        # origin_2 = ('Access-Control-Allow-Origin', 'http://test.xuanren360.com')
        methods = ('Access-Control-Allow-Methods', 'HEAD, OPTIONS, GET, POST, DELETE, PUT')
        credentials = ('Access-Control-Allow-Credentials', 'true')
        header = ('Access-Control-Allow-Headers', 'x-requested-with,content-type')
        if headers:
            headers.add(*origin)
            # headers.add(*origin_1)
            # headers.add(*origin_2)
            headers.add(*methods)
            headers.add(*credentials)
            headers.add(*header)
        else:
            headers = Headers([origin, methods, credentials, header])
        kwargs['headers'] = headers
        super(MyResponse, self).__init__(response, **kwargs)



# class WenFaDevelopmentConfig(Config):
#     ABS_PATH = './assets'
#     SQLALCHEMY_DATABASE_URI = os.environ.get(
#         'DATABASE_URI') or 'mysql+pymysql://winner_robot:winnerwinnerrobot0134@127.0.0.1/DevWinnerWinnerRobot'
#     SQLALCHEMY_BINDS = {'android_db': 'mysql+pymysql://winner_robot:winnerwinnerrobot0134@127.0.0.1/cia'}


config_map = {
    'production': ProductionConfig,
    'dev': DevelopmentConfig,
    'test': TestConfig,
    # 'zwf_dev': WenFaDevelopmentConfig
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
config_name_s = 'p'

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
    print("目前没有该环境")
    config_name = 'zwf_dev'
    raise NotImplementedError
else:
    raise ValueError

app = Flask(__name__)
app.config.from_object(config_map[config_name])
# 跨域，替换flask原有response，注释下方语句即可关闭
app.response_class = MyResponse
config = config_map[config_name]
db = SQLAlchemy(app, session_options={"autoflush": False})

# DB_SERVER_URL = u'http://dal.com:8090/'
DB_SERVER_URL = u'http://dal.ixuanren.com/'
if ENV == "PRODUCTION":
    DB_SERVER_URL = u'http://dal.com:8090/'

rds = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 1, password = "redisRedis_789")

APP_YACA = "yaca"
APP_ZIDOU = "zidou"
APP_TEST = "test"

APP_INFO_DICT = dict()
# APP_DICT = dict()
APP_INFO_DICT[APP_YACA] = {"APP_ID": "wxc3bc48b4c40651fd", "APP_SECRET": "959f45dbf812a5685f85ff572e76a671", "URL_ORI": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc3bc48b4c40651fd&redirect_uri=http%3a%2f%2fwx.walibee.com%2fauth.html&response_type=code&scope=snsapi_userinfo&state={}#wechat_redirect"}
# APP_INFO_DICT[APP_ZIDOU] = {"APP_ID": "wxc8b40fcec9626528", "APP_SECRET": "6e63c26d856f7ecb1779f24ab2fc08f4", "URL_ORI": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc8b40fcec9626528&redirect_uri=http%3a%2f%2fzidouwx.xuanren360.com%2fauth.html&response_type=code&scope=snsapi_userinfo&state={}#wechat_redirect"}
APP_INFO_DICT[APP_ZIDOU] = {"APP_ID": "wxbe0f84cc2b873c72", "APP_SECRET": "d6063862625c0a79719bc6167503f35e", "URL_ORI": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxbe0f84cc2b873c72&redirect_uri=http%3a%2f%2fwx.zidouchat.com%2fauth.html&response_type=code&scope=snsapi_userinfo&state={}#wechat_redirect"}
APP_INFO_DICT[APP_TEST] = {"APP_ID": "wxc8b40fcec9626528", "APP_SECRET": "6e63c26d856f7ecb1779f24ab2fc08f4", "URL_ORI": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc8b40fcec9626528&redirect_uri=http%3a%2f%2fwx.ixuanren.com%2fauth.html&response_type=code&scope=snsapi_userinfo&state={}#wechat_redirect"}
# APP_INFO_DICT[APP_ZIDOUBOT] = {"APP_ID": "wxc8b40fcec9626528", "APP_SECRET": "6e63c26d856f7ecb1779f24ab2fc08f4", "URL_ORI": "https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxc8b40fcec9626528&redirect_uri=http%3a%2f%2fzidouwx.xuanren360.com%2fauth.html&response_type=code&scope=snsapi_userinfo&state={}#wechat_redirect"}
# APP_DICT['http://test2.xuanren360.com'] = APP_YACA
# APP_DICT['http://www.xuanren360.com'] = APP_YACA


# TODO 此处应换为新公众号的数值
APP_ID = 'wxc3bc48b4c40651fd'
APP_SECRET = '959f45dbf812a5685f85ff572e76a671'

main_api = Blueprint('api', __name__)
main_api_v2 = Blueprint('api_v2', __name__)

# 生成所有任务的循环和发送所有任务的循环所需要用的时间
PRODUCTION_CIRCLE_INTERVAL = 1
CONSUMPTION_CIRCLE_INTERVAL = 1
CRAWLER_CIRCLE_INTERVAL = 300
TIMED_BATCH_SENDING_INTERVAL = 3 * 60
VIP_CHECK_INTERVAL = 30 * 60

# 错误代码
ERROR_CODE = dict()
# 正常
SUCCESS = 'success'
ERROR_CODE[SUCCESS] = {'status_code': 0}

# 机器人死掉
BOT_DEAD = 'dead_bot'
ERROR_CODE[BOT_DEAD] = {'status_code': -100190}
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
# 功能未实现，先留出口
ERR_NOT_IMPLEMENTED = 'err_not_implemented'
ERROR_CODE[ERR_NOT_IMPLEMENTED] = {'discription': '功能未实现，先留出口', 'status_code': -16}

# 成员不存在
ERR_INVALID_MEMBER = 'err_invalid_member'
ERROR_CODE[ERR_NOT_IMPLEMENTED] = {'discription': '成员不存在', 'status_code': -17}

# PC 已登录
ERR_ALREADY_LOGIN = 'err_already_login'
ERROR_CODE[ERR_ALREADY_LOGIN] = {'discription': '成员不存在', 'status_code': -18}

# 手机号不合法
ERR_INVALID_PHONE = 'err_invalid_phone'
ERROR_CODE[ERR_INVALID_PHONE] = {'discription': '手机号不合法', 'status_code': -19}

# SMS_CODE 过期
ERR_SMS_CODE_EXPIRED = 'err_sms_code_expired'
ERROR_CODE[ERR_SMS_CODE_EXPIRED] = {'discription': 'SMS_CODE 过期', 'status_code': -20}

# SMS_CODE 错误
ERR_INVALID_SMS_CODE = 'err_invalid_sms_code'
ERROR_CODE[ERR_INVALID_SMS_CODE] = {'discription': 'SMS_CODE 错误', 'status_code': -21}

# INVALID_URL
ERR_INVALID_URL = 'err_invalid_url'
ERROR_CODE[ERR_INVALID_URL] = {'discription': 'URL 不合法', 'status_code': -22}

# NOT_ALLOWED_EXTENSION
ERR_NOT_ALLOWED_EXTENSION = 'err_not_allowed_extension'
ERROR_CODE[ERR_NOT_ALLOWED_EXTENSION] = {'discription': '文件类型错误', 'status_code': -23}

# 建立默认分组时已有默认分组
WARN_HAS_DEFAULT_QUN = 'warn_has_default_qun'
ERROR_CODE[WARN_HAS_DEFAULT_QUN] = {'discription': '建立默认分组时已有默认分组', 'status_code': 1}

# 遇到被try到的未知错误
CRITICAL_HAS_EXCEPT = 'critical_has_except'
ERROR_CODE[CRITICAL_HAS_EXCEPT] = {'discription': '遇到被try到的未知错误', 'status_code': -1001}

# 该用户目前无正在使用中的bot
INFO_NO_USED_BOT = 'info_no_used_bot'
ERROR_CODE[INFO_NO_USED_BOT] = {'discription': '该用户目前无正在使用中的bot', 'status_code': 20001}

# 定时时间太短
SHORT_DURATION_TIME_ERROR = 'too_short_time_duration'
ERROR_CODE[SHORT_DURATION_TIME_ERROR] = {'discription': '设置时间太短', 'status_code': -10086}
# 导出文件内容为空
EMPTY_CONTENT = 'EMPTY_CONTENT'
ERROR_CODE[EMPTY_CONTENT] = {'discription': '文件内容为空', 'status_code': -10010}

#URL 请求错误
URL_ERROR = 'URL_ERROR'
ERROR_CODE[URL_ERROR] = {'discription': 'URL请求错误', 'status_code': -24}



# 用户的token过期时间（单位为日）
TOKEN_EXPIRED_THRESHOLD = 365

# consumption类型
CONSUMPTION_TASK_TYPE = {"batch_sending_task": 1,
                         "auto_reply": 2,
                         "daily_bonus": 3,
                         "welcome_message": 4,
                         "real_time_quotes": 5,
                         "synchronous_announcement": 6,
                         "instruction_when_into_a_qun": 7}

# 发送内容的类型；1为文字；2为图片；3为链接；4为文件；5为小程序；6为公众号；7为视频；8为语音
TASK_SEND_TYPE = {
    "text": 1,
    "picture": 2,
    "link": 3,
    "file": 4,
    "mini_programs": 5,
    "massive_platform": 6,
    "video": 7,
    "voice": 8,
    "update_chatroom_members_info": 950701,
    "update_members_info": 950702
}

# 全局匹配规则更新标记，每次更新规则库需将锁打开
GLOBAL_RULES_UPDATE_FLAG = dict()
GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG = "global_user_matching_rules_update_flag"
GLOBAL_RULES_UPDATE_FLAG.setdefault(GLOBAL_USER_MATCHING_RULES_UPDATE_FLAG, True)
GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG = "global_matching_default_rules_update_flag"
GLOBAL_RULES_UPDATE_FLAG.setdefault(GLOBAL_MATCHING_DEFAULT_RULES_UPDATE_FLAG, True)
GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG = "global_sensitive_word_rules_flag"
GLOBAL_RULES_UPDATE_FLAG.setdefault(GLOBAL_SENSITIVE_WORD_RULES_UPDATE_FLAG, True)
GLOBAL_EMPLOYEE_PEOPLE_FLAG = 'global_employee_people_flag'
GLOBAL_RULES_UPDATE_FLAG.setdefault(GLOBAL_EMPLOYEE_PEOPLE_FLAG, True)

GLOBAL_NOTICE_UPDATE_FLAG = "global_notice_update_flag"
GLOBAL_RULES_UPDATE_FLAG.setdefault(GLOBAL_NOTICE_UPDATE_FLAG, {})
GLOBAL_RULES_UPDATE_FLAG[GLOBAL_NOTICE_UPDATE_FLAG].setdefault("block.cc", True)

MATERIAL_TYPE_TXT = 1
MATERIAL_TYPE_PIC = 2
MATERIAL_TYPE_VIDEO = 3
MATERIAL_TYPE_VOICE = 4
MATERIAL_TYPE_LINK = 5
MATERIAL_TYPE_FILE = 6
MATERIAL_TYPE_MINIP = 7

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
MSG_TYPE_ENTERCHATROOM = 570425393

CONTENT_TYPE_UNKNOWN = -1
CONTENT_TYPE_TXT = 1
CONTENT_TYPE_PIC = 3
CONTENT_TYPE_MP3 = 34
CONTENT_TYPE_NAME_CARD = 42
CONTENT_TYPE_MP4 = 43
CONTENT_TYPE_GIF = 47
CONTENT_TYPE_VIDEO = 62
CONTENT_TYPE_SHARE = 49
CONTENT_TYPE_SYS = 10000
CONTENT_TYPE_RED = -10001
CONTENT_TYPE_ENTERCHATROOM = 570425393

CONTENT_TYPE_NAMES = {
    CONTENT_TYPE_TXT: u'文本',CONTENT_TYPE_PIC: u'图片',
    CONTENT_TYPE_MP3: u'语音',
    CONTENT_TYPE_NAME_CARD: u'名片',
    CONTENT_TYPE_MP4: u'视频',
    CONTENT_TYPE_GIF: u'表情',
    CONTENT_TYPE_VIDEO: u'视频',
    CONTENT_TYPE_SHARE: u'分享',
    CONTENT_TYPE_SYS: u'系统消息',
    CONTENT_TYPE_RED: u'红包',
}

WS_MAP = dict()

MAX_MEMBER_COUNT_DECIMAL = Decimal(500)

SCOPE_YES = -1
SCOPE_MINUTE = 60
SCOPE_HOUR = 3600
SCOPE_TODAY = 1
SCOPE_24_HOUR = 24
SCOPE_WEEK = 7
SCOPE_MONTH = 30
SCOPE_ALL = 0

DEFAULT_SCOPE_LIST = [SCOPE_ALL, SCOPE_24_HOUR, SCOPE_WEEK, SCOPE_MONTH]

DEFAULT_PAGE = 0
DEFAULT_PAGE_SIZE = 2

USER_CHATROOM_R_PERMISSION_1 = 1  # 管理员
USER_CHATROOM_R_PERMISSION_2 = 2  # 非管理员

CRON_TYPE_CHATROOM_OVERVIEW = 1
CRON_TYPE_CHATROOM_STATISTIC = 2
CRON_TYPE_MEMBER_OVERVIEW = 3

LEVEL_CLASS = ['D', 'C', 'B', 'A']

DB_RULE = dict()
JsapiTicket = "jsapi_ticket"
AccessToken = "access_token"
UserInfo = "client_member"
UserSwitch = "client_switch"
UserBotR = "client_bot_r"
BotInfo = "bot_info"
UserQunR = "client_qun_r"
UserGroupR = "client_group_r"
Chatroom = "a_chatroom"
Member = "a_member"
Contact = "a_contact"
Keywords = "keywords"
Message = "a_message"
Coin = "coin"
Wallet = "wallet"
BatchSendTask = "batch_send_task"
Client = "client"
MaterialLib = "material_lib"
ShareTask = "share_task"
ShareRecord = "share_record"
MPMember = "mp_member"
StatisticsShareTask = "statistics_share_task"

SECRET_ATTR_SET = {"chatroomname", "username", "bot_username"}

CHAT_LOGS_TYPE_0 = 0  # 退群
CHAT_LOGS_TYPE_1 = 1  # 拉人进群
CHAT_LOGS_TYPE_2 = 2  # 发言不带@
CHAT_LOGS_TYPE_3 = 3  # 发言带@

CHAT_LOGS_ERR_TYPE_0 = 0  # 未匹配到昵称和 wxid 的关系
CHAT_LOGS_ERR_TYPE_1 = 1  # 匹配到多个昵称和 wxid 的关系

BATCH_SEND_TASK_STATUS_1 = 1  # 等待中
BATCH_SEND_TASK_STATUS_2 = 2  # 发送中
BATCH_SEND_TASK_STATUS_3 = 3  # 成功
BATCH_SEND_TASK_STATUS_4 = 4  # 失败

NEW_MSG_Q = Queue()

SIGN_DICT = dict()
SENSITIVE_WORD_RULE_DICT = dict()

TURING_API_URL = u"http://www.tuling123.com/openapi/api"

ANDROID_SERVER_URL_BOT_STATUS = u"http://ardsvr.ixuanren.com/android/bot_status"
ANDROID_SERVER_URL_SEND_MASS_MESSAGE = u"http://ardsvr.ixuanren.com/android/send_mass_message"
ANDROID_SERVER_URL_SEND_MESSAGE = u"http://ardsvr.ixuanren.com/android/send_message"
ANDROID_SERVER_URL = u"http://ardsvr.ixuanren.com"

if ENV == 'PRODUCTION':
    ANDROID_SERVER_URL_BOT_STATUS = u"http://ardsvr.xuanren360.com/android/bot_status"
    ANDROID_SERVER_URL_SEND_MASS_MESSAGE = u"http://ardsvr.xuanren360.com/android/send_mass_message"
    ANDROID_SERVER_URL_SEND_MESSAGE = u"http://ardsvr.xuanren360.com/android/send_message"
    ANDROID_SERVER_URL = u"http://ardsvr.xuanren360.com"

# aliyun
REGION = "cn-hangzhou"  # 暂时不支持多region
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"
# ACCESS_KEY_ID/ACCESS_KEY_SECRET 根据实际申请的账号信息进行替换
ACCESS_KEY_ID = "LTAIN1QF1zEIhADM"
ACCESS_KEY_SECRET = "VDpxavKUCNgFyoAijdTKcGKQqkrNgp"

acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

DES_TIMELINE = 1
DES_APP_MSG = 2
DES_QQ = 3
DES_WEIBO = 4
DES_QZONE = 5

DES_LIST = (DES_TIMELINE, DES_APP_MSG, DES_QQ, DES_WEIBO, DES_QZONE)
DES_DICT = {
    DES_TIMELINE: 'timeline',
    DES_APP_MSG: 'app_msg',
    DES_QQ: 'qq',
    DES_WEIBO: 'weibo',
    DES_QZONE: 'qzone',
}
DES_NAME_DICT = {
    DES_TIMELINE: '朋友圈',
    DES_APP_MSG: '微信好友',
    DES_QQ: 'QQ 好友',
    DES_WEIBO: '微博',
    DES_QZONE: 'QQ 空间',
}

SHARE_RECORD_CLICK = 0
SHARE_RECORD_SHARE = 1

ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif', 'jpeg'}

OSS_KEY = "LTAIfwRTXLl6vMbX"
OSS_SECRET = "kvSS9E4Ty7nvHHlGukaknJUtfICuen"
BUCKET_NAME = "ywbdthumb"
OSS_ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
OSS_THUMB = '?x-oss-process=style/thumb'

URL_TYPE_TEMP = 0
URL_TYPE_AD_IFRAM = 1
URL_TYPE_AD_DIRECT = 2


SHARE_TASK_ORDER = ["", "create_time", "clicked_uv", "clicked_pv", "shared_uv", "shared_pv"]
# SHARE_TASK_CLICKED_UV = 1
# SHARE_TASK_CLICKED_PV = 2
# SHARE_TASK_SHARED_UV = 3
# SHARE_TASK_SHARED_PV = 4

DES_SECRET = "multiple"
