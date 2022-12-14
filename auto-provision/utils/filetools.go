package util

import (
	"fmt"
	"io/ioutil"
	"os"
)

func ReadFile(filePath string) (fileContent string) {
	file, err := os.Open(filePath)
	if err != nil {
		panic(err)
	}
	defer func(file *os.File) {
		err := file.Close()
		if err != nil {
			panic(err)
		}
	}(file)
	content, err := ioutil.ReadAll(file)
	fmt.Println(string(content))
	return string(content)
}
