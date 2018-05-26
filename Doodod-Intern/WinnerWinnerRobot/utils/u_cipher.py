# -*- coding: utf-8 -*-
import base64
import logging

from Crypto.Cipher import PKCS1_v1_5, DES
from Crypto.PublicKey import RSA

from configs.config import DES_SECRET
from utils.u_model_json_str import unicode_to_str
from utils.u_transformat import str_to_unicode

logger = logging.getLogger('main')

with open('public.pem', "r") as f:
    public_pem = f.read()
with open('private.pem') as f:
    private_pem = f.read()


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


def des_encryt(text, b64_flag = True):
    cipher = DES.new(DES_SECRET, DES.MODE_ECB)
    remainder = len(text) % 8
    text += u"*" * (8 - remainder)
    print text
    cipher_text = cipher.encrypt(unicode_to_str(text))
    if b64_flag:
        cipher_text = base64.b64encode(cipher_text)
    return cipher_text


def des_decrypt(cipher_text, b64_flag = True):
    cipher = DES.new(DES_SECRET, DES.MODE_ECB)
    if b64_flag:
        cipher_text = base64.b64decode(cipher_text)
    text = cipher.decrypt(cipher_text)
    print text
    text = text.rstrip(u"*")
    return text
