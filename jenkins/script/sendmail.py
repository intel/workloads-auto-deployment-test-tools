#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
import smtplib
# import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, receiver_emails: list, smtp, port, password, html, subject):

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)

    # Create the plain-text and HTML version of your message
    # html = """\
    # <html>
    # <body>
    #     <p>Hi,<br>
    #     How are you?<br>
    #     </p>
    # </body>
    # </html>
    # """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)

    # Create secure connection with server and send email
    # context = ssl.create_default_context()
    # with smtplib.SMTP_SSL("smtp.intel.com", 25, context=context) as server:
    # smtp = "smtp.intel.com"
    # port = 25
    with smtplib.SMTP(smtp, port) as server:
        server.user = sender_email
        server.password = password
        server.auth_plain()
        server.sendmail(
            sender_email, receiver_emails, message.as_string()
        )