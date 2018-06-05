# -*- coding: utf-8 -*-
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
import time
import datetime
import os


log = ''
now_time = datetime.datetime.now()
now_time_str = now_time.strftime('%Y-%m-%d')
yes_time = now_time + datetime.timedelta(days=-1)
yes_time_str = yes_time.strftime('%Y-%m-%d')
abs_path = '/www/WinnerWinnerRobot/'

if time.localtime().tm_hour >= 12:
    #中午12点的错误报告发送，如果log文件中log时间是当天就直接发送，不然不发送
    with open('%slogs/procedure_error.log'%abs_path,'r') as f:
        log = f.read()
        if log[:10] != now_time_str:
            print '本日12点前没有错误log'
            log = ''
else:
    #半夜0点的错误报告发送
    #先判断log文件是否已经分片
    new_log_switch = False
    with open('%slogs/procedure_error.log'%abs_path,'r') as f:
        tmp = f.read()
        if tmp[:10] == now_time_str:
            new_log_switch = True
    path = None
    if new_log_switch:
        #如果已分片， 读取前一天log
        if os.path.exists('%slogs/procedure_error.log.%s'%(abs_path,yes_time_str)):

            path = '%slogs/procedure_error.log.%s'%(abs_path,yes_time_str)
    else:
        #如果未分片， 读取当前log
        path = '%slogs/procedure_error.log'%abs_path
    if path:
        with open(path,'r') as f:
            tmp_log = f.read().split('\n')
            after12 = False
            for line in tmp_log:
                if line[:10] == yes_time_str and line[11:13] >= '12':
                    after12 = True
                if after12:
                    log += line + '\n'
    else:
        print '昨日12点后无错误log'

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

if log != '':
        
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
    print "已发送%s的log"%now_time_str







