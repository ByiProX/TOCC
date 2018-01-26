# -*- coding: utf-8 -*-

import logging
import hashlib

from datetime import datetime, timedelta

from config import db, SUCCESS, TOKEN_EXPIRED_THRESHOLD, ERR_USER_TOKEN_EXPIRED, ERR_USER_LOGIN_FAILED
from core.wechat import WechatConn
from models.user_bot import UserInfo

logger = logging.getLogger('main')

wechat_conn = WechatConn()


class UserLogin:
    def __init__(self, code):
        self.code = code
        self.open_id = ""
        self.user_access_token = ""
        self.now_user_info = UserInfo()
        self.user_info_up_to_date = UserInfo()

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
        self._get_open_id_and_user_access_token()
        whether_is_new, self.now_user_info = self._check_is_new_user()

        if self.open_id is not None:
            if whether_is_new is True:
                self._add_new_user()
                return SUCCESS, self.user_info_up_to_date.token
            else:
                self._update_user()
                return SUCCESS, self.user_info_up_to_date.token
        else:
            if whether_is_new is False:
                if str(datetime.now()) < self.now_user_info.token_expired_time:
                    return SUCCESS, self.now_user_info.token
                else:
                    return ERR_USER_TOKEN_EXPIRED, None
            else:
                return ERR_USER_LOGIN_FAILED, None

    def _check_is_new_user(self):
        if self.open_id is None:
            raise ValueError("没有正确的open_id")

        user_info = db.session.query(UserInfo).filter(UserInfo.open_id == self.open_id).first()
        if user_info is None:
            return True
        else:
            return False

    def _add_new_user(self):
        self._get_user_info_from_wechat()

        self.user_info_up_to_date.token = self._generate_user_token()
        self.user_info_up_to_date.token_expired_time = datetime.now() + timedelta(days=TOKEN_EXPIRED_THRESHOLD)

        self.user_info_up_to_date.create_time = datetime.now()

        db.session.add(self.user_info_up_to_date)
        db.session.commit()

    def _update_user(self):
        # TODO 更新用户信息
        # 包括更新token
        self._update_new_user_token_into_mysql()
        pass

    def _get_user_info_from_wechat(self):

        if self.open_id is None or self.user_access_token is None:
            raise ValueError("没有正确的open_id和user_access_token")
        res_json = wechat_conn.get_user_info(open_id=self.open_id, user_access_token=self.user_access_token)

        self.user_info_up_to_date = UserInfo()
        if res_json.get('openid'):
            self.user_info_up_to_date.open_id = res_json.get('openid')
            self.user_info_up_to_date.nick_name = res_json.get('nick_name')
            self.user_info_up_to_date.sex = res_json.get('sex')
            self.user_info_up_to_date.province = res_json.get('province')
            self.user_info_up_to_date.city = res_json.get('city')
            self.user_info_up_to_date.country = res_json.get('country')
            self.user_info_up_to_date.avatar_url = res_json.get('avatar_url')
            self.user_info_up_to_date.union_id = res_json.get('unionid')
            self.user_info_up_to_date.code = res_json.get('code')

    def _update_new_user_token_into_mysql(self):
        # TODO 将user_token更新，然后放入mysql
        # 如果没过期，则不更新
        # 如果过期了，则需要更新
        pass

    def _generate_user_token(self):
        if self.open_id is None:
            raise ValueError("没有正确的open_id")
        pre_str = self.open_id.upper() + str(datetime.now()) + "stvrhu"
        m2 = hashlib.md5()
        m2.update(pre_str)
        token = m2.hexdigest()
        return token
