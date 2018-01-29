# -*- coding: utf-8 -*-

import logging
import hashlib

from datetime import datetime, timedelta

from config import db, SUCCESS, TOKEN_EXPIRED_THRESHOLD, ERR_USER_TOKEN_EXPIRED, ERR_USER_LOGIN_FAILED, ERR_USER_TOKEN
from core.wechat import WechatConn
from models.user_bot import UserInfo

logger = logging.getLogger('main')

wechat_conn = WechatConn()


class UserLogin:
    def __init__(self, code):
        self.code = code
        self.open_id = ""
        self.user_access_token = ""
        self.now_user_info = None
        self.user_info_up_to_date = None

        self._get_open_id_and_user_access_token()

    def _get_open_id_and_user_access_token(self):
        """
        根据前端微信返回的code，去wechat的api处调用open_id
        """
        res_json = wechat_conn.get_open_id_by_code(code=self.code)
        self.open_id = res_json.get('openid')
        self.user_access_token = res_json.get('access_token')

    def get_user_token(self):
        """
        从微信处得到open_id，然后通过open得到token
        """
        # 如果没有读取到open_id
        if self.open_id is None:
            self.now_user_info = db.session.query(UserInfo).filter(UserInfo.code == self.code).first()
            # 如果这个code和上次code一样
            if self.now_user_info:
                if datetime.now() < self.now_user_info.token_expired_time:
                    return SUCCESS, self.now_user_info
                else:
                    return ERR_USER_TOKEN_EXPIRED, None
            # 如果这个code在库中查不到
            else:
                return ERR_USER_LOGIN_FAILED, None
        else:
            self._get_user_info_from_wechat()
            # 抓到了信息，那么所有信息都更新
            if self.user_info_up_to_date:
                self.now_user_info = db.session.query(UserInfo).filter(UserInfo.open_id == self.open_id).first()
                # 意味着之前有，现在也有
                if self.now_user_info:
                    self.user_info_up_to_date.code = self.code
                    self.user_info_up_to_date.last_login_time = datetime.now()

                    if datetime.now() < self.now_user_info.token_expired_time:
                        pass
                    else:
                        self.user_info_up_to_date.token = self._generate_user_token()
                        self.user_info_up_to_date.token_expired_time = datetime.now() + timedelta(
                            days=TOKEN_EXPIRED_THRESHOLD)

                    db.session.merge(self.user_info_up_to_date)
                    db.session.commit()
                    return SUCCESS, self.user_info_up_to_date
                else:
                    self.user_info_up_to_date.code = self.code
                    self.user_info_up_to_date.create_time = datetime.now()
                    self.user_info_up_to_date.last_login_time = datetime.now()

                    self.user_info_up_to_date.token = self._generate_user_token()
                    self.user_info_up_to_date.token_expired_time = datetime.now() + timedelta(
                        days=TOKEN_EXPIRED_THRESHOLD)

                    self.user_info_up_to_date.func_send_qun_messages = False
                    self.user_info_up_to_date.func_qun_sign = False
                    self.user_info_up_to_date.func_auto_reply = False
                    self.user_info_up_to_date.func_welcome_message = False

                    db.session.add(self.user_info_up_to_date)
                    db.session.commit()
                    return SUCCESS, self.user_info_up_to_date

            # 因为各种原因没有拿到用户信息
            else:
                self.now_user_info = db.session.query(UserInfo).filter(UserInfo.open_id == self.open_id).first()
                if self.now_user_info:
                    if datetime.now() < self.now_user_info.token_expired_time:
                        return SUCCESS, self.now_user_info
                    else:
                        return ERR_USER_TOKEN_EXPIRED, None
                else:
                    return ERR_USER_LOGIN_FAILED, None

    @staticmethod
    def verify_token(token):
        user_info = db.session.query(UserInfo).filter(UserInfo.token == token).first()
        if user_info:

            if datetime.now() < user_info.token_expired_time:
                return SUCCESS
            else:
                return ERR_USER_TOKEN_EXPIRED
        else:
            return ERR_USER_TOKEN

    def _get_user_info_from_wechat(self):
        res_json = wechat_conn.get_user_info(open_id=self.open_id, user_access_token=self.user_access_token)

        if res_json.get('openid'):
            self.user_info_up_to_date = UserInfo()
            self.user_info_up_to_date.open_id = res_json.get('openid')
            self.user_info_up_to_date.union_id = res_json.get('unionid')
            self.user_info_up_to_date.nick_name = res_json.get('nick_name')
            self.user_info_up_to_date.sex = res_json.get('sex')
            self.user_info_up_to_date.province = res_json.get('province')
            self.user_info_up_to_date.city = res_json.get('city')
            self.user_info_up_to_date.country = res_json.get('country')
            self.user_info_up_to_date.avatar_url = res_json.get('avatar_url')

        # 获取wechat端信息失败
        else:
            pass

    def _generate_user_token(self, open_id=None, datetime_now=None):
        if open_id and datetime_now:
            self.open_id = open_id
            datetime_now = datetime_now
        else:
            datetime_now = datetime.now()

        if self.open_id is None:
            raise ValueError("没有正确的open_id")

        pre_str = self.open_id.upper() + str(datetime_now) + "stvrhu"
        m2 = hashlib.md5()
        m2.update(pre_str)
        token = m2.hexdigest()
        return token
