# -*- coding: utf-8 -*-
import base64
import copy
import json
import urllib

import time

import sys
from unicodedata import normalize

import re

import requests
from flask import request, abort
from configs.config import *
from core_v2.user_core import UserLogin
from core_v2.wechat_core import wechat_conn_dict
from models_v2.base_model import BaseModel, CM
from utils.u_model_json_str import verify_json
from utils.u_response import make_response
import logging

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

    mp_member = CM(MPMember).from_json(user_info.to_json_full())
    mp_member.create_time = int(time.time())
    mp_member.save()
    open_id = mp_member.open_id

    thumb_url = request.json.get("thumb_url")
    desc = request.json.get("desc")
    url_type = request.json.get("url_type")

    share_task = CM(ShareTask)
    share_task.is_deleted = 0
    share_task.ori_url = ori_url
    share_task.title = title
    share_task.thumb_url = thumb_url
    share_task.desc = desc
    share_task.client_id = client_id
    share_task.url_type = url_type
    share_task.create_time = int(time.time())
    share_task.update_time = int(time.time())
    share_task.save()

    state_json = generate_state_json(user_info.app, share_task.share_task_id, ori_id = open_id, ref_id = "0", cur_id = open_id, hierarchy = 0)

    share_task.state_json = state_json
    share_task.update()

    return make_response(SUCCESS, share_task = share_task.to_json_full(), state_json = state_json)


@main_api_v2.route("/get_share_list", methods = ['POST'])
def api_get_share_list():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    page = request.json.get("page", DEFAULT_PAGE)
    pagesize = request.json.get("pagesize", DEFAULT_PAGE_SIZE)

    share_list = BaseModel.fetch_all(ShareTask, "*", where_clause = BaseModel.where_dict({"client_id": user_info.client_id,
                                                                                          "is_deleted": 0}), page = page, pagesize = pagesize, order_by = BaseModel.order_by({"create_time": "desc"}))
    share_list_json = [r.to_json_full() for r in share_list]

    return make_response(SUCCESS, share_list = share_list_json)


@main_api_v2.route("/share_task", methods = ['POST'])
def api_share_task():
    verify_json()
    status, user_info = UserLogin.verify_token(request.json.get('token'))
    if status != SUCCESS:
        return make_response(status)

    state = request.json.get("state")

    app_name, share_task_id, ori_id, ref_id, cur_id, hierarchy, des_id = extract_share_state(state)
    share_record = CM(ShareRecord)
    share_record.share_task_id = share_task_id
    share_record.ori_id = ori_id
    share_record.ref_id = ref_id
    share_record.cur_id = cur_id
    share_record.hierarchy = int(hierarchy)
    share_record.des_id = des_id
    share_record.type = SHARE_RECORD_SHARE
    share_record.create_time = int(time.time())
    share_record.save()

    return make_response(SUCCESS)


@main_api_v2.route("/get_state_by_state", methods = ['POST'])
def api_get_state_by_state():
    verify_json()
    code = request.json.get('code')
    state = request.json.get('state')

    if not state:
        return make_response(ERR_INVALID_PARAMS)

    app_name, share_task_id, ori_id, ref_id, cur_id, hierarchy, des_id = extract_share_state(state)

    share_task = BaseModel.fetch_by_id(ShareTask, share_task_id)
    if not code:
        return make_response(SUCCESS, share_task = share_task.to_json_full())

    regist_status, mp_member = mp_member_regist(code, app_name)
    ref_id = cur_id
    hierarchy = int(hierarchy) + 1
    cur_id = mp_member.open_id

    share_record = CM(ShareRecord)
    share_record.share_task_id = share_task_id
    share_record.ori_id = ori_id
    share_record.ref_id = ref_id
    share_record.cur_id = cur_id
    share_record.hierarchy = hierarchy
    share_record.des_id = des_id
    share_record.type = SHARE_RECORD_CLICK
    share_record.create_time = int(time.time())
    share_record.save()

    state_json = generate_state_json(app_name, share_task_id, ori_id, ref_id, cur_id, hierarchy)

    return make_response(SUCCESS, share_task = share_task.to_json_full(), state_json = state_json)


def generate_state_json(app_name, share_task_id, ori_id, ref_id, cur_id, hierarchy):
    state = 'app=' + str(app_name) + '&task=' + str(share_task_id) + '&ori=' + str(ori_id) + '&ref=' + str(ref_id) + '&cur=' + str(cur_id) + '&hierarchy=' + str(hierarchy)

    state_json = dict()
    for des_id in DES_LIST:
        state_tmp = copy.deepcopy(state)
        state_tmp += '&des=' + str(des_id)
        state_tmp = urllib.quote(state_tmp)
        state_tmp = base64.b64encode(state_tmp)
        state_json[DES_DICT[des_id]] = state_tmp
    return state_json


def extract_share_state(share_state):
    state_tmp = urllib.unquote(base64.b64decode(share_state))
    params = state_tmp.split('&')
    state_json = dict()
    for param in params:
        key, value = param.split('=')
        state_json.setdefault(key, value)

    app_name = state_json.get('app')
    share_task_id = state_json.get('task')
    ori_id = state_json.get('ori')
    ref_id = state_json.get('ref')
    cur_id = state_json.get('cur')
    hierarchy = state_json.get('hierarchy')
    des_id = state_json.get('des')
    logger.info('task_id: ' + str(share_task_id))
    logger.info('ori_id: ' + str(ori_id))
    logger.info('ref_id: ' + str(ref_id))
    logger.info('cur_id: ' + str(cur_id))
    logger.info('hierarchy: ' + str(hierarchy))
    logger.info('des_id: ' + str(des_id))

    return app_name, share_task_id, ori_id, ref_id, cur_id, hierarchy, des_id


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


def mp_member_regist(code, app_name):
    we_conn = wechat_conn_dict.get(app_name)
    if we_conn is None:
        logger.info(
            u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (app_name, json.dumps(wechat_conn_dict.keys())))
    res_json = we_conn.get_open_id_by_code(code = code)
    open_id = res_json.get('openid')
    user_access_token = res_json.get('access_token')
    if open_id is None:
        logger.error(ERR_USER_LOGIN_FAILED +
                     u"code微信不认可，库中无该code. code: %s. app: %s." % (code, app_name))
        return ERR_USER_LOGIN_FAILED, None
    else:
        mp_member = BaseModel.fetch_one(MPMember, "*", where_clause = BaseModel.where_dict({"open_id": open_id,
                                                                                            "app": app_name}))
        if mp_member:
            logger.info(u"已经注册，nickname: %s" % mp_member.nick_name)
            return SUCCESS, mp_member
        we_conn = wechat_conn_dict.get(app_name)
        if we_conn is None:
            logger.info(
                u"没有找到对应的 app: %s. wechat_conn_dict.keys: %s." % (app_name, json.dumps(wechat_conn_dict.keys())))
        res_json = we_conn.get_user_info(open_id = open_id, user_access_token = user_access_token)

        if res_json.get('openid'):
            mp_member = CM(MPMember)
            mp_member.open_id = res_json.get('openid')
            mp_member.union_id = res_json.get('unionid')
            mp_member.nick_name = res_json.get('nickname')
            mp_member.sex = res_json.get('sex')
            mp_member.province = res_json.get('province')
            mp_member.city = res_json.get('city')
            mp_member.country = res_json.get('country')
            mp_member.avatar_url = res_json.get('avatar_url')
            mp_member.app = app_name

            mp_member.save()

            return SUCCESS, mp_member
        # 获取wechat端信息失败
        else:
            return ERR_WRONG_ITEM, None
