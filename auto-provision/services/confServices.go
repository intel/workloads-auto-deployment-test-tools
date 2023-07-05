/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
package services

import (
	config "api-provision/conf"
	"api-provision/models"
	"api-provision/utils"
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"text/template"
	"time"

	"github.com/gin-gonic/gin"
)

func StrContains(origStr, destStr string) bool {
	if strings.Contains(origStr, destStr) {
		return true
	} else {
		return false
	}
}

func Sub(number1, number2 int) int {
	return number1 - number2
}

func TemplateConf(conf models.ProversionConf, constTemplate string, filePath string) {
	t := template.Must(template.New("sh").Funcs(template.FuncMap{"strcontains": StrContains, "sub": Sub}).Parse(constTemplate))
	err := t.Execute(os.Stdout, conf)
	if err != nil {
		log.Println("Executing template:", err)
	}
	file, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		log.Printf("open file failed %s", err)
	}
	err = t.Execute(file, conf)
	if err != nil {
		return
	}
	defer func(file *os.File) {
		err := file.Close()
		if err != nil {
			return
		}
	}(file)
}

func shellTask(baseGenFilePath string, err error, conf models.ProversionConf) {
	// TODO exec job
	ctxJob, cancel := context.WithCancel(context.Background())
	go func(cancelFunc context.CancelFunc) {
		time.Sleep(30 * time.Second)
		cancelFunc()
	}(cancel)

	shellCmd1 := fmt.Sprintf("chmod +x %s*", baseGenFilePath)
	err = util.CommandShell(ctxJob, shellCmd1)
	if err != nil {
		panic(err)
	}
	jobId := conf.JobId
	jobLog := fmt.Sprintf("%s%s%s%s%s", config.ProjectPath, "output/log/", jobId, "-", "provision.log")
	startProvisionCmd := fmt.Sprintf("./start.sh %s-workload", jobId)
	execPath := fmt.Sprintf("%s%s", config.ProjectPath, "task")
	shellCmd2 := fmt.Sprintf("cd %s;%s>%s", execPath, startProvisionCmd, jobLog)
	err = util.CommandShell(ctxJob, shellCmd2)
	if err != nil {
		panic(err)
	}
}

func CreateConf(ctx *gin.Context) {
	conf := models.ProversionConf{}
	err := ctx.BindJSON(&conf)
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"msg": err,
		})
	}
	conf.BiosArgs = updateBiosArgs(conf)
	baseGenFilePath := config.TaskConfPath + conf.JobId + "-workload"
	TemplateConf(conf, config.TemplateSh, baseGenFilePath+".sh")
	TemplateConf(conf, config.TemplateYaml, baseGenFilePath+".yaml")
	TemplateConf(conf, config.TemplateInventory, baseGenFilePath+".ini")
	go shellTask(baseGenFilePath, err, conf)
	ctx.JSON(http.StatusOK, gin.H{
		"msg": "The configuration file has been generated and the task has started",
	})

}

func updateBiosArgs(conf models.ProversionConf) []models.BiosArgs {
	BiosArgsSupport := map[string]string{
		"Intel(R) Hyper-Threading Tech":    "ProcessorHyperThreadingDisable",
		"LLC Prefetch":                     "LlcPrefetchEnable",
		"Intel(R) VT for Directed I/O":     "VTdSupport",
		"Enhanced Intel SpeedStep(R) Tech": "ProcessorEistEnable",
		"Intel(R) Turbo Boost Technology":  "TurboMode",
		"Energy Efficient Turbo":           "EETurboDisable",
		"Hardware P-States":                "ProcessorHWPMEnable",
		"C1E":                              "ProcessorC1eEnable",
		"Processor C6":                     "C6Enable",
		"SR-IOV Support":                   "SRIOVEnable",
		"AVX P1":                           "AvxP1Level",
		"NUMA Optimized":                   "NumaEn",
		"SNC (Sub NUMA)":                   "SncEn",
	}
	oldBiosArgs := conf.BiosArgs
	var newBiosArgs []models.BiosArgs
	for _, biosArg := range oldBiosArgs {
		newBiosArgs = append(
			newBiosArgs,
			models.BiosArgs{
				Knob:   BiosArgsSupport[biosArg.Prompt],
				Prompt: biosArg.Prompt,
				Value:  biosArg.Value,
			})
	}
	return newBiosArgs
}
