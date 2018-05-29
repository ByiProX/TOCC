# -*- coding: utf-8 -*-
import base64
import cStringIO
import copy
import json
import logging
import re
import sys
import time
import traceback
import urllib
from unicodedata import normalize

import qrcode
import requests
from flask import request

from configs.config import *
from core_v2.user_core import UserLogin
from core_v2.wechat_core import wechat_conn_dict
from models_v2.base_model import BaseModel, CM
from utils.u_cipher import des_encryt, des_decrypt
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
from utils.u_upload_oss import put_file_to_oss

logger = logging.getLogger('main')


@main_api_v2.route("/upload_oss", methods = ['POST'])
def api_upload_oss():
    # verify_json()
    status, user_info = UserLogin.verify_token(request.form.get('token'))
    if status != SUCCESS:
        return make_response(status)

    upload_file = request.files['file']
    logger.info('upload filename: ' + upload_file.filename)
    if not upload_file or not allowed_file(upload_file.filename):
        return make_response(ERR_NOT_ALLOWED_EXTENSION)

    filename = str(user_info.client_id) + '_' + secure_filename(normalize('NFKD', upload_file.filename).encode('utf-8', 'ignore').decode('utf-8'))
    oss_url = put_file_to_oss(filename, data = upload_file.stream._file)

    return make_response(SUCCESS, oss_url = oss_url)


@main_api_v2.route("/create_share_task", methods = ['POST'])
def create_task():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    client_id = user_info.client_id
    ori_url = request.json.get("ori_url")
    title = request.json.get("title")
    if not ori_url or not title:
        return make_response(ERR_INVALID_PARAMS)

    response = requests.get(ori_url, verify = False)
    if not response or response.status_code != 200:
        return make_response(ERR_INVALID_URL)

    mp_member = BaseModel.fetch_one(MPMember, "*", where_clause = BaseModel.where_dict({"open_id": user_info.open_id,
                                                                                        "app": user_info.app}))
    if not mp_member:
        mp_member = CM(MPMember).from_json(user_info.to_json_full())
        mp_member.create_time = int(time.time())
        mp_member.mp_member_unique_id = mp_member.open_id[-5:] + unicode(mp_member.create_time)
        mp_member.save()

    thumb_url = request.json.get("thumb_url")
    desc = request.json.get("desc", ori_url)
    url_type = request.json.get("url_type")

    now = int(time.time())
    share_task = CM(ShareTask)
    share_task.task_id = unicode(user_info.client_id) + "_" + unicode(now)
    share_task.is_deleted = 0
    share_task.ori_url = ori_url
    share_task.title = title
    share_task.thumb_url = thumb_url
    share_task.desc = desc
    share_task.client_id = client_id
    share_task.url_type = url_type
    share_task.create_time = now
    share_task.update_time = now
    share_task.total_click_pv = 0
    share_task.total_click_uv = 0
    # share_task.total_click_list = []
    share_task.total_share_pv = 0
    share_task.total_share_uv = 0
    # share_task.total_share_list = []
    share_task.save()

    state_json = generate_state_json(share_task.task_id, ref_id = "0", cur_id = mp_member.mp_member_unique_id, hierarchy = 0)

    share_task.state_json = state_json
    share_task.update()

    return make_response(SUCCESS, share_task = share_task.to_json_full(), state_json = state_json)


@main_api_v2.route("/get_share_info", methods = ['POST'])
def api_get_share_info():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    task_id = request.json.get("task_id")
    if not task_id:
        return make_response(ERR_INVALID_PARAMS)
    share_task = BaseModel.fetch_one(ShareTask, "*", where_clause = BaseModel.where_dict({"task_id": task_id}))
    if not share_task:
        return make_response(ERR_WRONG_ITEM)

    return make_response(SUCCESS, share_task = share_task.to_json_full())


@main_api_v2.route("/get_share_list", methods = ['POST'])
def api_get_share_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    page = request.json.get("page", DEFAULT_PAGE)
    pagesize = request.json.get("pagesize", DEFAULT_PAGE_SIZE)

    total_count = BaseModel.count(ShareTask, where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                  "is_deleted": 0}))
    share_list = BaseModel.fetch_all(ShareTask, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                          "is_deleted": 0}), page = page, pagesize = pagesize, order_by = BaseModel.order_by({"create_time": "desc"}))
    share_list_json = [r.to_json_full() for r in share_list]

    return make_response(SUCCESS, share_list = share_list_json, total_count = total_count)


@main_api_v2.route("/share_task", methods = ['POST'])
def api_share_task():
    verify_json()
    # mp_member_id = request.json.get("mp_member_id")

    state = request.json.get("state")
    app_name = request.json.get("app")

    if not app_name:
        return make_response(ERR_INVALID_PARAMS)

    task_id, ref_id, cur_id, hierarchy, des_id = extract_share_state(state)

    share_record = CM(ShareRecord)
    share_record.task_id = task_id
    share_record.ref_id = ref_id
    share_record.cur_id = cur_id
    share_record.hierarchy = int(hierarchy)
    share_record.des_id = des_id
    share_record.type = SHARE_RECORD_SHARE
    share_record.create_time = int(time.time())
    share_record.save()

    if ref_id == "0":
        return make_response(SUCCESS)

    statistic_mp_member(task_id, ref_id, cur_id, hierarchy, des_id, SHARE_RECORD_SHARE)
    share_task = BaseModel.fetch_one(ShareTask, "*", where_clause = BaseModel.where_dict({"task_id": task_id}))
    if not share_task:
        return make_response(ERR_WRONG_ITEM)

    if share_task.total_share_pv is None:
        share_task.total_share_pv = 0
    share_task.total_share_pv += 1
    if share_task.total_share_list is None:
        share_task.total_share_list = list()
    if cur_id not in share_task.total_share_list:
        share_task.total_share_list.append(cur_id)
    share_task.total_share_uv = len(share_task.total_share_list)

    share_task.update_time = int(time.time())
    share_task.update()

    return make_response(SUCCESS)


@main_api_v2.route("/get_state_by_state", methods = ['POST'])
def api_get_state_by_state():
    verify_json()
    code = request.json.get('code')
    state = request.json.get('state')
    app_name = request.json.get('app', "test")

    if not state or not app_name:
        return make_response(ERR_INVALID_PARAMS)

    task_id, ref_id, cur_id, hierarchy, des_id = extract_share_state(state)

    share_task = BaseModel.fetch_one(ShareTask, "*", where_clause = BaseModel.where_dict({"task_id": task_id}))
    if not code:
        return make_response(SUCCESS, share_task = share_task.to_json_full(), state_json = {})

    regist_status, mp_member = mp_member_regist(code, app_name, task_id)
    if regist_status != SUCCESS:
        return make_response(regist_status)

    ref_id = cur_id
    hierarchy = int(hierarchy) + 1
    cur_id = mp_member.mp_member_unique_id

    statistic_mp_member(task_id, ref_id, cur_id, hierarchy, des_id, SHARE_RECORD_CLICK)

    share_record = CM(ShareRecord)
    share_record.task_id = task_id
    share_record.ref_id = ref_id
    share_record.cur_id = cur_id
    share_record.hierarchy = hierarchy
    share_record.des_id = des_id
    share_record.type = SHARE_RECORD_CLICK
    share_record.create_time = int(time.time())
    share_record.save()

    if share_task.total_click_pv is None:
        share_task.total_click_pv = 0
    share_task.total_click_pv += 1
    if share_task.total_click_list is None:
        share_task.total_click_list = list()
    if cur_id not in share_task.total_click_list:
        share_task.total_click_list.append(cur_id)
    share_task.total_click_uv = len(share_task.total_click_list)

    share_task.update_time = int(time.time())
    share_task.update()

    state_json = generate_state_json(task_id, ref_id, cur_id, hierarchy)

    return make_response(SUCCESS, share_task = share_task.to_json_full(), state_json = state_json)


def generate_state_json(task_id, ref_id, cur_id, hierarchy):
    state = 't=' + str(task_id) + '&r=' + str(ref_id) + '&c=' + str(cur_id) + '&h=' + str(hierarchy)

    state_json = dict()
    for des_id in DES_LIST:
        state_tmp = copy.deepcopy(state)
        state_tmp += '&d=' + str(des_id)
        # state_tmp = des_encryt(state_tmp)
        state_tmp = base64.b64encode(state_tmp)
        state_tmp = urllib.quote(state_tmp)
        state_json[DES_DICT[des_id]] = state_tmp
    return state_json


def extract_share_state(share_state):
    try:
        # state_tmp = des_decrypt(urllib.unquote(share_state))
        state_tmp = urllib.unquote(share_state)
        state_tmp = base64.b64decode(state_tmp)
        params = state_tmp.split('&')
        state_json = dict()
        for param in params:
            key, value = param.split('=')
            state_json.setdefault(key, value)

        task_id = state_json.get('t')
        ref_id = state_json.get('r')
        cur_id = state_json.get('c')
        hierarchy = state_json.get('h')
        des_id = state_json.get('d')
        logger.info('task_id: ' + str(task_id))
        logger.info('ref_id: ' + str(ref_id))
        logger.info('cur_id: ' + str(cur_id))
        logger.info('hierarchy: ' + str(hierarchy))
        logger.info('des_id: ' + str(des_id))

        return task_id, ref_id, cur_id, hierarchy, des_id
    except Exception as e:
        logger.critical("extract_share_state err")
        logger.critical(traceback.format_exc())
        logger.error(e)
        return None, None, None, None, None


# def generate_state_json(app_name, task_id, ori_id, ref_id, cur_id, hierarchy):
#     state = 'a=' + str(app_name) + '&t=' + str(task_id) + '&o=' + str(ori_id) + '&r=' + str(ref_id) + '&c=' + str(cur_id) + '&h=' + str(hierarchy)
#
#     state_json = dict()
#     for des_id in DES_LIST:
#         state_tmp = copy.deepcopy(state)
#         state_tmp += '&d=' + str(des_id)
#         state_tmp = des_encryt(state_tmp)
#         state_tmp = urllib.quote(state_tmp)
#         state_json[DES_DICT[des_id]] = state_tmp
#     return state_json
#
#
# def extract_share_state(share_state):
#     try:
#         state_tmp = des_decrypt(urllib.unquote(share_state))
#         params = state_tmp.split('&')
#         state_json = dict()
#         for param in params:
#             key, value = param.split('=')
#             state_json.setdefault(key, value)
#
#         app_name = state_json.get('a')
#         task_id = state_json.get('t')
#         ori_id = state_json.get('o')
#         ref_id = state_json.get('r')
#         cur_id = state_json.get('c')
#         hierarchy = state_json.get('h')
#         des_id = state_json.get('d')
#         logger.info('task_id: ' + str(task_id))
#         logger.info('ori_id: ' + str(ori_id))
#         logger.info('ref_id: ' + str(ref_id))
#         logger.info('cur_id: ' + str(cur_id))
#         logger.info('hierarchy: ' + str(hierarchy))
#         logger.info('des_id: ' + str(des_id))
#
#         return app_name, task_id, ori_id, ref_id, cur_id, hierarchy, des_id
#     except:
#         return None, None, None, None, None, None, None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def secure_filename(filename):
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename(u'i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you generate random
    filename if the function returned an empty one.

    .. versionadded:: 0.5

    :param filename: the filename to secure
    """
    if isinstance(filename, str):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('utf-8', 'ignore')
        PY2 = sys.version_info[0] == 2
        if not PY2:
            filename = filename.decode('utf-8')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    _filename_gbk_strip_re = re.compile(u"[^\u4e00-\u9fa5A-Za-z0-9_.-]")
    filename = _filename_gbk_strip_re.sub('', '_'.join(
                   filename.split())).encode('utf-8').strip('._')
    # filename = _filename_gbk_strip_re.sub('', '_'.join(
    #                filename.split())).strip('._')

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                             'LPT2', 'LPT3', 'PRN', 'NUL')
    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename


def mp_member_regist(code, app_name, task_id):
    we_conn = wechat_conn_dict.get(app_name)
    if we_conn is None:
        logger.info(
            u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (app_name, json.dumps(wechat_conn_dict.keys())))
    res_json = we_conn.get_open_id_by_code(code = code)
    open_id = res_json.get('openid')
    user_access_token = res_json.get('access_token')
    if open_id is None:

        mp_member = BaseModel.fetch_one(UserInfo, '*', where_clause = BaseModel.where_dict({"code": code,
                                                                                            "app": app_name}))
        if mp_member:
            return SUCCESS, mp_member
        logger.error(ERR_USER_LOGIN_FAILED +
                     u"code微信不认可，库中无该code. code: %s. app: %s." % (code, app_name))
        return ERR_USER_LOGIN_FAILED, None
    else:

        now = int(time.time())
        mp_member = BaseModel.fetch_one(MPMember, "*", where_clause = BaseModel.where_dict({"open_id": open_id,
                                                                                            "app": app_name}))
        if not mp_member:
            we_conn = wechat_conn_dict.get(app_name)
            if we_conn is None:
                logger.info(
                    u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (app_name, json.dumps(wechat_conn_dict.keys())))
            res_json = we_conn.get_user_info(open_id = open_id, user_access_token = user_access_token)

            mp_member = CM(MPMember)
            mp_member.code = code
            mp_member.open_id = res_json.get('openid')
            mp_member.union_id = res_json.get('unionid')
            mp_member.nick_name = res_json.get('nickname')
            mp_member.sex = res_json.get('sex')
            mp_member.province = res_json.get('province')
            mp_member.city = res_json.get('city')
            mp_member.country = res_json.get('country')
            mp_member.avatar_url = res_json.get('headimgurl')
            mp_member.app = app_name
            mp_member.create_time = now
            mp_member.mp_member_unique_id = mp_member.open_id[-5:] + unicode(mp_member.create_time)
            mp_member.save()

            # Mark 先匹配昵称，匹配到多个则匹配头像
            # 这里有坑，匹配到一个也不能保证是同一个人

        mp_member.code = code
        mp_member.save()
        logger.info(u"已经注册，nickname: %s" % mp_member.nick_name)

        s_mp_memebr = BaseModel.fetch_one(StatisticsShareTask, "*",
                                          where_clause = BaseModel.where_dict({"task_id": task_id,
                                                                               "mp_member_unique_id": mp_member.mp_member_unique_id}))
        if not s_mp_memebr:
            s_mp_memebr = CM(StatisticsShareTask)
            s_mp_memebr.create_time = now
            s_mp_memebr.task_id = task_id
            s_mp_memebr.mp_member_unique_id = mp_member.mp_member_unique_id
            s_mp_memebr.clicked_uv = 0
            s_mp_memebr.clicked_pv = 0
            s_mp_memebr.shared_uv = 0
            s_mp_memebr.shared_pv = 0
            # s_mp_memebr.shared_list = []
            # s_mp_memebr.clicked_list = []
            s_mp_memebr.update_time = now
            s_mp_memebr.save()

        return SUCCESS, mp_member


@main_api_v2.route("/get_statistic_list", methods = ['POST'])
def api_get_statistic_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    task_id = request.json.get("task_id")
    if not task_id:
        return make_response(ERR_INVALID_PARAMS)
    share_task = BaseModel.fetch_one(ShareTask, "*", where_clause = BaseModel.where_dict({"task_id": task_id}))
    if not share_task:
        return make_response(ERR_WRONG_ITEM)

    page = request.json.get("page", DEFAULT_PAGE)
    pagesize = request.json.get("pagesize", DEFAULT_PAGE_SIZE)
    order_by = request.json.get("order_by", 1)
    order_by = SHARE_TASK_ORDER[order_by]
    order = "desc"

    total_count = BaseModel.count(StatisticsShareTask, where_clause = BaseModel.where_dict({"task_id": task_id}))
    statistic_list = BaseModel.fetch_all(StatisticsShareTask, "*", where_clause = BaseModel.where_dict({"task_id": task_id}), page = page, pagesize = pagesize, order_by = BaseModel.order_by({order_by: order}))
    statistic_list_json = list()
    for statistic in statistic_list:
        statistic_json = statistic.to_json_full()
        mp_member = BaseModel.fetch_one(MPMember, "*", where_clause = BaseModel.where_dict({"mp_member_unique_id": statistic.mp_member_unique_id}))
        if mp_member:
            mp_member_json = mp_member.to_json_full()
            mp_member_json.update(statistic_json)
            statistic_list_json.append(mp_member_json)
        else:
            statistic_list_json.append(statistic_json)

    return make_response(SUCCESS, share_task = share_task.to_json_full(), statistic_list = statistic_list_json, total_count = total_count)


@main_api_v2.route('/get_url_qrcode', methods = ['POST'])
def get_qrcode():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    content = request.json.get('url')

    qr = qrcode.QRCode(
        version = 3,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size = 8,
        border = 3,
    )
    qr.add_data(content)
    qr.make()
    img = qr.make_image()
    buffer = cStringIO.StringIO()
    img.save(buffer, format = "JPEG")
    img_str = base64.b64encode(buffer.getvalue())

    return make_response(SUCCESS, img = img_str)


def statistic_mp_member(task_id, ref_id, cur_id, hierarchy, des_id, action_type = None):
    now = int(time.time())
    # if ref_id == "0" or cur_id == ref_id:
    #     return None
    ref_s_mp_memebr = BaseModel.fetch_one(StatisticsShareTask, "*", where_clause = BaseModel.where_dict({"task_id": task_id,
                                                                                                         "mp_member_unique_id": ref_id}))
    if not ref_s_mp_memebr:
        ref_s_mp_memebr = CM(StatisticsShareTask)
        ref_s_mp_memebr.create_time = now
        ref_s_mp_memebr.task_id = task_id
        ref_s_mp_memebr.mp_member_unique_id = ref_id
        ref_s_mp_memebr.clicked_uv = 0
        ref_s_mp_memebr.clicked_pv = 0
        ref_s_mp_memebr.shared_uv = 0
        ref_s_mp_memebr.shared_pv = 0
        # ref_s_mp_memebr.shared_list = []
        # ref_s_mp_memebr.clicked_list = []
    ref_s_mp_memebr.update_time = now

    if action_type == SHARE_RECORD_SHARE:
        ref_s_mp_memebr.shared_pv += 1
        if ref_s_mp_memebr.shared_list is None:
            ref_s_mp_memebr.shared_list = [cur_id]
        else:
            if cur_id in ref_s_mp_memebr.shared_list:
                pass
            else:
                ref_s_mp_memebr.shared_list.append(cur_id)
                ref_s_mp_memebr.shared_uv += 1
    elif action_type == SHARE_RECORD_CLICK:
        ref_s_mp_memebr.clicked_pv += 1
        if ref_s_mp_memebr.clicked_list is None:
            ref_s_mp_memebr.clicked_list = [cur_id]
        else:
            if cur_id in ref_s_mp_memebr.clicked_list:
                pass
            else:
                ref_s_mp_memebr.clicked_list.append(cur_id)
                ref_s_mp_memebr.clicked_uv += 1

    ref_s_mp_memebr.save()

    return ref_s_mp_memebr


@main_api_v2.route("/get_share_signature", methods=['POST'])
def get_share_signature():
    verify_json()
    url = request.json.get("url")

    # mp_member_id = request.json.get("mp_member_id")
    app_name = request.json.get("app")

    if url is None:
        return make_response(ERR_INVALID_PARAMS)
    try:
        we_conn = wechat_conn_dict.get(app_name)
        if we_conn is None:
            logger.info(
                u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (app_name, json.dumps(wechat_conn_dict.keys())))
        timestamp, noncestr, signature = we_conn.get_signature_from_access_token(url)
        return make_response(SUCCESS, timestamp=timestamp, noncestr=noncestr, signature=signature)
    except Exception as e:
        logger.error('ERROR  %s' % e)
        return make_response(ERR_INVALID_PARAMS)
