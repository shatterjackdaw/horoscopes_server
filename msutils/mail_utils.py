# coding:utf-8
import smtplib
from email.mime.text import MIMEText


def send_mail(to_list, sub, content):
    mail_host = "smtp.exmail.qq.com"  # 设置服务器
    mail_user = "sys_op@mobile-mafia.com"  # 用户名
    mail_pass = "Youputao2012"  # 口令
    mail_postfix = "mobile-mafia.com"  # 发件箱的后缀

    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = mail_user
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(mail_user, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False
