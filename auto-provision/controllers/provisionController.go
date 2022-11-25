package controller

import (
	services "api-provision/services"

	"github.com/gin-gonic/gin"
)

type ConfController struct{}

func (confController ConfController) GetConf(ctx *gin.Context) {
	services.CreateConf(ctx)
}

type FileController struct{}

func (fileController FileController) UploadFile(ctx *gin.Context) {
	services.UploadFile(ctx)
}

func (fileController FileController) DownloadFile(ctx *gin.Context) {
	services.DownloadFile(ctx)
}

type StatusMachine struct{}

func (statusMachine StatusMachine) StatusProgress(ctx *gin.Context) {
	services.StatusProgress(ctx)
}
