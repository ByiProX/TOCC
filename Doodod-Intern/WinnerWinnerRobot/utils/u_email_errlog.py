# -*- coding: utf-8 -*-
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
import time
import re

log = ''
if time.localtime().tm_hour < 12:
    with open('/www/WinnerWinnerRobot/logs/procedure_error.log','r') as f:
        log = f.read()
else:
    with open('/www/WinnerWinnerRobot/logs/procedure_error.log','r') as f:
        r = f.read().split('\n')
        new_log_switch = False
        for line in r:
            if not new_log_switch and re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}',line) and line[11:13] >= '12':
                new_log_switch = True
            if new_log_switch:
                log += line + '\n'

mail_info = {
    "from": "zidoubot@doodod.com",
    "to": ["wutianjie@doodod.com","panshaoning@doodod.com","zhaochang@doodod.com",
        "zhangyunhao@doodod.com","konghao@doodod.com","wangkunxiang@doodod.com","lilei@doodod.com"],
    "hostname": "smtp.exmail.qq.com",
    "username": "zidoubot@doodod.com",
    "password": "Robot123",
    "mail_subject": "Errlog_%s"%time.strftime("%Y-%m-%d-%H:%M", time.localtime()) ,
    "mail_text": log,
    "mail_encoding": "utf-8"
}

if len(log) != 0:
        
    smtp = SMTP_SSL(mail_info["hostname"])
    smtp.set_debuglevel(1)
    
    smtp.ehlo(mail_info["hostname"])
    smtp.login(mail_info["username"], mail_info["password"])

    msg = MIMEText(mail_info["mail_text"], "plain", mail_info["mail_encoding"])
    msg["Subject"] = Header(mail_info["mail_subject"], mail_info["mail_encoding"])
    msg["from"] = mail_info["from"]
    for receiver in mail_info["to"]:
        smtp.sendmail(mail_info["from"], receiver, msg.as_string())

    smtp.quit()







