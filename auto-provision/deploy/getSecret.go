package main

import (
	"api-provision/conf"
	"context"
	"fmt"
	"log"

	vault "github.com/hashicorp/vault/api"
)

func GetVaultSecret() (data map[string]interface{}) {
	config := vault.DefaultConfig()
	config.Address = conf.VaultServerAddress
	client, err := vault.NewClient(config)
	if err != nil {
		log.Fatalf("unable to initialize Vault client: %v", err)
	}
	client.SetToken(conf.VaultToken)
	// Read a secret
	//secret, err := client.KVv2("secret").Get(ctx, "my-secret-password")
	ctx := context.Background()
	secret, err := client.KVv1("kv").Get(ctx, "wsf-secret-password")
	if err != nil {
		log.Fatalf("unable to read secret: %v", err)
	}

	return secret.Data
}

func main() {
	secretData := GetVaultSecret()
	fmt.Println(secretData)
	fmt.Println("jenkinsUserName::", secretData["jenkinsUserName"])
	fmt.Println("jenkinsToken::", secretData["jenkinsToken"])
	fmt.Println("jenkinsUrl::", conf.JenkinsUrl)
	fmt.Println("statusUrl::", conf.StatusUrl)
	fmt.Println("portalUserName::", secretData["portalUserName"])
	fmt.Println("portalPassword::", secretData["portalPassword"])
        fmt.Println("SMTPServer::", conf.SMTPServer)
        fmt.Println("SMTPPort::", conf.SMTPPort)
        fmt.Println("JfrogUrl::", conf.JfrogUrl)
}
