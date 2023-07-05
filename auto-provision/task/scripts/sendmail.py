#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr

import pathlib
import click

#mail_host = "smtp.intel.com"
#mail_port = 25


@click.command()
@click.option('-s', default='xxxx@intel.com', help='sender')
@click.option('-r', default='xxxx@intel.com', help='receiver')
@click.option('-c', default='this is auto email form intel', help='message content')
@click.option('-m', default='', help='smtp server')
@click.option('-p', default='25', help='smtp port')
@click.option('-f', default=None, help='attachment path')
def send_email(s, r, c, m ,p, f):
    
    r = r.replace(" ", "")
    r = r.split(",")
    c = c.replace("===", " ")
    title = '[Notice]Workloads auto deployment test tools execution report'
    if f:
        message = MIMEMultipart()
        part_text = MIMEText(c)
        message.attach(part_text)
        attach = MIMEApplication(open(f, 'rb').read())
        attach.add_header('Content-Disposition', 'attachment',
                          filename=pathlib.Path(f).name)
        message.attach(attach)
    else:
        message = MIMEText(c, 'html', 'utf-8')
    #message['From'] = "{}".format(s)
    message["From"] = Header(s, 'utf-8')
    #message["From"] = __format_addr('NPG-WiE-Benchmarking-Report@intel.com')
    message['To'] = ",".join(r)
    message['Subject'] = title
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(m, int(p))
        #smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.sendmail(s, r, message.as_string())
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)


send_email()
