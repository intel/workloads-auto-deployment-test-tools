/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
package main

import (
	"api-provision/conf"
	"api-provision/middleware"
	"github.com/gin-gonic/gin"
)

func main() {
	defaultLog(true)
	gin.SetMode(gin.DebugMode)
	r := gin.Default()
	r.Use(middleware.Logger())
	// r.Use(middleware.CrosHandler())
	// r.Use(middleware.TlsHandler(listenAddress))
	middleware.Jwt().MiddlewareFunc()
	regRouters(r)
	graceShutdown(r, conf.ListenAddress)
}
