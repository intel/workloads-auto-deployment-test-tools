package test

import (
	config "api-provision/conf"
	"fmt"
	"testing"
)

func TestConfig(t *testing.T) {
	fmt.Println(config.ListenAddress)
	fmt.Println(config.VaultServerAddress)
	fmt.Println(config.VaultToken)
	fmt.Println(config.Https)
	fmt.Println(config.ProjectPath)
}
