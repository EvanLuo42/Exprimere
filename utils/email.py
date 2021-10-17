import smtplib
from email.header import Header
from email.mime.text import MIMEText


def send_captcha(captcha):
    mail_host = 'smtp.163.com'
    mail_user = 'luo_evan@163.com'
    mail_pass = 'IIXDHTNPEYHUXGIY'
    sender = 'luo_evan@163.com'
    receivers = captcha.email

    message = MIMEText('您的验证码为:' + captcha.captcha, 'plain', 'utf-8')
    message['From'] = '<luo_evan@163.com>'
    message['To'] = '<' + captcha.email + '>'

    subject = 'Exprimere 验证码'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtp_obj = smtplib.SMTP()
        smtp_obj.connect(mail_host, 25)
        smtp_obj.login(mail_user, mail_pass)
        smtp_obj.sendmail(sender, receivers, str(message))
        return True
    except smtplib.SMTPException:
        return False
