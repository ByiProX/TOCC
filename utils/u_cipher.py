# -*- coding: utf-8 -*-
import base64
import logging

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

from configs.config import public_pem, private_pem
from utils.u_model_json_str import unicode_to_str
from utils.u_transformat import str_to_unicode

logger = logging.getLogger('main')


def rsa_encrypt(text):
    rsakey = RSA.importKey(public_pem)  # 导入读取到的公钥
    cipher = PKCS1_v1_5.new(rsakey)  # 生成对象
    cipher_text = base64.b64encode(cipher.encrypt(unicode_to_str(text)))
    return cipher_text


def rsa_decrypt(cipher_text):
    rsakey = RSA.importKey(private_pem)  # 导入读取到的私钥
    cipher = PKCS1_v1_5.new(rsakey)  # 生成对象
    text = cipher.decrypt(base64.b64decode(cipher_text), "ERROR")
    return str_to_unicode(text)
