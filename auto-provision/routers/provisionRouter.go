/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
package routers

import (
	controller "api-provision/controllers"
	"api-provision/middleware"
	"log"

	jwt "github.com/appleboy/gin-jwt/v2"
	"github.com/gin-gonic/gin"
)

func AuthRouter(r *gin.Engine) {
	authMiddleware := middleware.Jwt()
	{
		r.NoRoute(authMiddleware.MiddlewareFunc(), func(c *gin.Context) {
			claims := jwt.ExtractClaims(c)
			log.Printf("NoRoute claims: %#v\n", claims)
			c.JSON(404, gin.H{
				"code":    "PAGE_NOT_FOUND",
				"message": "Page not found",
			})
		})
		r.POST("/login", authMiddleware.LoginHandler)
		r.GET("/refreshtoken", authMiddleware.RefreshHandler)
	}
}
func ConfRouter(r *gin.Engine) {
	confRouters := r.Group("/conf")
	confRouters.Use(middleware.Jwt().MiddlewareFunc())
	{
		// curl -X POST localhost:8089/conf/createconf
		// curl -H "Content-Type: application/json" -X POST -d @conf.json localhost:8089/conf/createconf
		confRouters.POST("/createconf", controller.ConfController{}.GetConf)
	}

}

func FileRouter(r *gin.Engine) {

	r.MaxMultipartMemory = 100 << 20
	fileRouters := r.Group("/file")
	fileRouters.Use(middleware.Jwt().MiddlewareFunc())
	{
		/*
			curl -X POST http://localhost:8089/file/upload \
				  -F "upload[]=@test1.zip" \
				  -F "upload[]=@test2.zip" \
				  -H "Content-Type: multipart/form-data"
		*/
		fileRouters.POST("/upload", controller.FileController{}.UploadFile)
		/*
			curl -X POST localhost:8089/file/download/provision.log/35
		*/
		fileRouters.POST("/download/:filename/:jobid", controller.FileController{}.DownloadFile)
	}
}

func StatusMachineRouter(r *gin.Engine) {

	statusMachineRouters := r.Group("/statusmachine")
	statusMachineRouters.Use(middleware.Jwt().MiddlewareFunc())
	/*
		curl localhost:8089/statusmachine/statusprogress
	*/
	{
		statusMachineRouters.GET("/statusprogress", controller.StatusMachine{}.StatusProgress)
	}
}
