# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header

from utils.u_transformat import str_to_unicode

# 输入SMTP服务器地址:
smtp_server = "smtp.exmail.qq.com"
smtp_port = 465

# 输入Email地址和口令:
from_addr = "zidoubot@doodod.com"
password = "Robot123"

# 用户产品警报
ue_alert = "ue_alert@doodod.com"

# 技术运维警报
it_alert = "it_alert@doodod.com"


class EmailAlert:
    def __init__(self):
        pass

    @staticmethod
    def send_ue_alert(e_text, e_subject=None):
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.set_debuglevel(1)
        server.login(from_addr, password)

        msg = MIMEText(e_text, 'plain', 'utf-8')
        msg['From'] = u"紫豆机器人 <%s>" % from_addr
        msg['To'] = u"用户使用警报 <%s>" % ue_alert
        if not e_subject:
            e_subject = "警报邮件"
        msg['Subject'] = Header(str_to_unicode(e_subject), 'utf-8').encode()

        server.sendmail(from_addr, [ue_alert], msg.as_string())
        server.quit()

    @staticmethod
    def send_it_alert(e_text, e_subject=None):
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        # server.set_debuglevel(1)
        server.login(from_addr, password)

        msg = MIMEText(e_text, 'plain', 'utf-8')
        msg['From'] = u"紫豆机器人 <%s>" % from_addr
        msg['To'] = u"用户使用警报 <%s>" % it_alert
        if not e_subject:
            e_subject = "警报邮件"
        msg['Subject'] = Header(str_to_unicode(e_subject), 'utf-8').encode()

        server.sendmail(from_addr, [it_alert], msg.as_string())
        server.quit()
