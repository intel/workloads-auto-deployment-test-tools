package conf

import (
	models "api-provision/models"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path"
	"runtime"
)

func GetCurrentAbPathByCaller() string {
	var abPath string
	_, filename, _, ok := runtime.Caller(0)
	if ok {
		abPath = path.Dir(filename)
		return abPath
	} else {
		panic("not find the config file")
		return "error"
	}
}

func getConfig(configFilePath string) models.JsonConf {
	jsonFile, err := os.Open(configFilePath)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("Successfully Opened json config file")
	defer func(jsonFile *os.File) {
		err := jsonFile.Close()
		if err != nil {
			panic(err)
		}
	}(jsonFile)
	byteValue, _ := ioutil.ReadAll(jsonFile)
	var jsonConf models.JsonConf
	json.Unmarshal(byteValue, &jsonConf)
	return jsonConf
	//fmt.Println(jsonConf.Server.Address)
}

// var configFilePath = "./conf/conf.json"
var configFilePath = fmt.Sprintf("%s/conf.json", GetCurrentAbPathByCaller())
var configObj = getConfig(configFilePath)

var ListenAddress = configObj.Server.Address
var VaultServerAddress = configObj.Vault.Url
var VaultToken = configObj.Vault.Token
var Https = configObj.Server.Https
var ProjectPath = configObj.Server.Path
var TaskConfPath = fmt.Sprintf("%s%s", ProjectPath, "task/conf/")
var LogPath = fmt.Sprintf("%s%s", ProjectPath, "output/log/api-provision.log")
var UploadPath = fmt.Sprintf("%s%s", ProjectPath, "output/uploadfile/")
var JenkinsUrl = configObj.Jenkins.Url
var StatusUrl = configObj.Status.Url
var SMTPServer = configObj.Mail.Host
var SMTPPort = configObj.Mail.Port
var JfrogUrl = configObj.Jfrog.Url
