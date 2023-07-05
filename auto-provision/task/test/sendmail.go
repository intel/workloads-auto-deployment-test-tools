/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
package model

import (
	"fmt"
	"net/smtp"
	"strings"
)

func SendToMail(userName, password, mailServer, to, subject, body, mailType string) error {

	// 拼接消息体
	var contentType string
	if mailType == "html" {
		contentType = "Content-Type: text/" + mailType + "; charset=UTF-8"
	} else {
		contentType = "Content-Type: text/plain" + "; charset=UTF-8"
	}
	msg := []byte("To: " + to + "\r\nFrom: " + userName + "\r\nSubject: " + subject + "\r\n" + contentType + "\r\n\r\n" + body)

	// msg 内容输出查看
	fmt.Println("To: " + to + "\r\n" +
		"From: " + userName + "\r\n" +
		"Subject: " + subject + "\r\n" +
		"" + contentType + "\r\n\r\n" +
		"" + body)

	// 进行身份认证
	hp := strings.Split(mailServer, ":")
	auth := smtp.PlainAuth("", userName, password, hp[0])

	sendTo := strings.Split(to, ";")
	err := smtp.SendMail(mailServer, auth, userName, sendTo, msg)
	return err
}

func main() {
	var userName = "***@163.com"
	var password = "***"
	var mailServer = "smtp.163.com:25"
	var to = "**@qq.com"
	var subject = "犀点意象安全团队"

	body := `
		您的服务存在异常，请查收！！！
		`
	bodyHtml := `<html>
					<body>
						<h1>您的服务存在异常</h1>
					</body>
				</html>
				`
	fmt.Println("send email")
	var err error
	err = SendToMail(userName, password, mailServer, to, subject, body, "")
	if err != nil {
		fmt.Println("Send text-mail error!")
		fmt.Println(err)
	} else {
		fmt.Println("Send text-mail success!")
	}
	err = SendToMail(userName, password, mailServer, to, subject, bodyHtml, "html")
	if err != nil {
		fmt.Println("Send html-mail error!")
		fmt.Println(err)
	} else {
		fmt.Println("Send html-mail success!")
	}
}
