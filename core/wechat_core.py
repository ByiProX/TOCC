# -*- coding: utf-8 -*-

import logging
import requests
from datetime import datetime
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from configs.config import db
from configs.config import APP_ID, APP_SECRET
from models.user_bot_models import AccessToken
from utils.u_model_json_str import unicode_to_str

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logger = logging.getLogger('main')


class WechatConn:
    def __init__(self):
        self.access_token = db.session.query(AccessToken).first()

    def wechat_get(self, url, **kwargs):
        return self._wechat_requst('GET', url=url, **kwargs)

    def wechat_post(self, url, **kwargs):
        return self._wechat_requst('POST', url=url, **kwargs)

    @staticmethod
    def _wechat_requst(method, url, **kwargs):
        logger.info(u'url: ' + url)
        kwargs['verify'] = False
        res = requests.request(method=method, url=url, **kwargs)
        print(res.content)
        print(str(res.content))
        logger.info('res: ' + str(res.content))
        return res

    # 获取基础 access_token
    def get_access_token(self):
        now = datetime.now()

        if not self.access_token or self.access_token.expired_time <= now:
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + \
                  APP_ID + '&secret=' + APP_SECRET

            res = self.wechat_get(url=url)
            res_json = json.loads(res.content, strict=False)

            if self.access_token is None:
                access_token = AccessToken().load_from_json(res_json)
                db.session.add(access_token)
            else:
                self.access_token.load_from_json(res_json)
            db.session.commit()

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
