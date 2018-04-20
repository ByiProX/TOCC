# -*- coding: utf-8 -*-

import logging
import requests
from datetime import datetime
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from configs.config import APP_ID, APP_SECRET, AccessToken
from models_v2.base_model import BaseModel, CM
from utils.u_model_json_str import unicode_to_str

import random
import string
import time
import hashlib

# 禁用安全请求警告
from utils.u_time import datetime_to_timestamp_utc_8

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logger = logging.getLogger('main')


class WechatConn:
    def __init__(self):
        try:
            self.access_token = BaseModel.fetch_one(AccessToken, '*', where_clause = BaseModel.where(">", "expired_time", datetime_to_timestamp_utc_8(datetime.now())))
        except Exception, ex:
            self.access_token = None
            _msg = ex.message
            print _msg

    def wechat_get(self, url, **kwargs):
        return self._wechat_requst('GET', url=url, **kwargs)

    def wechat_post(self, url, **kwargs):
        return self._wechat_requst('POST', url=url, **kwargs)

    @staticmethod
    def _wechat_requst(method, url, **kwargs):
        logger.info(u'url: ' + url)
        kwargs['verify'] = False
        res = requests.request(method=method, url=url, **kwargs)
        logger.info('res: ' + str(res.content))
        return res

    # 获取基础 access_token
    def get_access_token(self):
        # now = datetime.now()
        now = int(time.time())

        if not self.access_token or self.access_token.expired_time <= now:
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + \
                  APP_ID + '&secret=' + APP_SECRET

            res = self.wechat_get(url=url)
            res_json = json.loads(res.content, strict=False)

            if self.access_token is None:
                self.access_token = CM(AccessToken)
            self.access_token.token = res_json.get("access_token")
            self.access_token.expired_time = now + res_json.get("expires_in")
            self.access_token.save()

        return self.access_token

        # 获取 open_id, 通过 code

    def get_open_id_by_code(self, code):
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=' + \
              APP_ID + '&secret=' + APP_SECRET + '&code=' + code + '&grant_type=authorization_code'
        res = self.wechat_get(url=url)
        res_json = json.loads(res.content, strict=False)
        return res_json

    def get_user_info(self, open_id, user_access_token):
        url = 'https://api.weixin.qq.com/sns/userinfo?access_token=' + \
              user_access_token + '&openid=' + open_id + '&lang=zh_CN'
        res = self.wechat_get(url=url)
        res_json = json.loads(res.content, strict=False)
        return res_json

    def _send_to_follower(self, data):
        access_token = self.get_access_token()
        url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=' + str(access_token.token)
        headers = {
            'content-type': 'application/json;charset=utf-8'
        }
        _ = self.wechat_post(url=url, data=json.dumps(data, ensure_ascii=False), headers=headers)

    def send_txt_to_follower(self, content, to_open_id):
        to_open_id = unicode_to_str(to_open_id)
        content = unicode_to_str(content)
        data = {
            "msgtype": "text",
            "touser": to_open_id,
            "text": {"content": content}
        }
        self._send_to_follower(data)

    def send_img_to_follower(self, media_id, to_open_id):
        to_open_id = unicode_to_str(to_open_id)
        media_id = unicode_to_str(media_id)
        data = {
            "touser": to_open_id,
            "msgtype": "image",
            "image": {"media_id": media_id}
        }
        self._send_to_follower(data)

    @staticmethod
    def wrap_url(url, txt):
        url = unicode_to_str(url)
        txt = unicode_to_str(txt)
        wrapped_url = '<a href="' + url + '"> ' + txt + '</a>'
        return wrapped_url

    #### add by quentintin
    # reference:
    # https: // mp.weixin.qq.com / wiki?t = resource / res_main & id = mp1421141115
    def get_access_token_V2(self):
        now = int(time.time())
        if not self.access_token or self.access_token.expired_time <= now:
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + \
                  APP_ID + '&secret=' + APP_SECRET

            res = self.wechat_get(url=url)
            res_json = json.loads(res.content, strict=False)

            if self.access_token is None:
                self.access_token = CM(AccessToken)
                self.access_token.token = res_json.get("access_token")
                self.access_token.expired_time = now + res_json.get("expires_in")
                self.access_token.save()
                return self.access_token.token
            elif self.access_token.expired_time <= now:
                self.access_token = BaseModel.fetch_all('access_token', '*')[0]
                self.access_token.token = res_json.get("access_token")
                self.access_token.expired_time = now + res_json.get("expires_in")
                self.access_token.update()
                return self.access_token.token
        else:
            return self.access_token.token

    def get_signature_from_access_token(self, url):
        try:
            access_token = self.get_access_token_V2()
        except Exception as e:
            logger.error('get_access_token ERROR %s' % e)
            return
        jsapi_ticket_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % access_token

        try:
            res = self.wechat_get(jsapi_ticket_url)
            args = {'jsapi_ticket': json.loads(res.content).get('ticket'),
                    'noncestr': ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)),
                    'timestamp': int(time.time()),
                    'url': url
            }
        except Exception as e:
            logger.error('wechat_get(jsapi_ticket_url) ERROR  %s' % e)
            return

        sorted_params = sorted(args.keys(), key=lambda d: d[0], reverse=False)
        joined_string = '&'.join([sorted_param + '=' + str(args[sorted_param]) for sorted_param in sorted_params])
        signature = hashlib.sha1(joined_string).hexdigest()

        return [args['timestamp'], args['noncestr'], signature]


wechat_conn = WechatConn()
