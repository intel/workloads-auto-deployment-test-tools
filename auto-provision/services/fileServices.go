package services

import (
	config "api-provision/conf"
	"api-provision/utils"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

func UploadFile(ctx *gin.Context) {
	// Multipart form
	form, _ := ctx.MultipartForm()
	files := form.File["upload[]"]
	dst := config.UploadPath
	for _, file := range files {
		log.Println(file.Filename)
		log.Println(file.Size)
		fmt.Println(dst + file.Filename)
		err := ctx.SaveUploadedFile(file, dst+file.Filename)
		if err != nil {
			ctx.JSON(http.StatusNotFound, gin.H{
				"msg": "file uploaded!",
			})
		}
	}
	ctx.JSON(http.StatusOK, gin.H{
		"msg": "file uploaded!",
	})

}

func DownloadFile(ctx *gin.Context) {
	logName := ctx.Param("filename")
	jobId := ctx.Param("jobid")
	filePath := fmt.Sprintf("%s%s%s%s%s", config.ProjectPath, "output/log/", jobId, "-", logName)
	log.Println(filePath)
	if !checkFileIsExist(filePath) {
		ctx.JSON(http.StatusNotFound, gin.H{
			"msg": "the file not found",
		})
	} else {
		ctx.JSON(http.StatusOK, gin.H{
			"logContent": util.ReadFile(filePath),
		})
		// ctx.File(filePath)
	}
}

func checkFileIsExist(filename string) bool {
	var exist = true
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		exist = false
	}
	return exist
}
