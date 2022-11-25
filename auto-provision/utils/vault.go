package util

import (
	"api-provision/conf"
	"context"
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
	// Authenticate
	// WARNING: This quickstart uses the root token for our Vault dev server.
	// Don't do this in production!
	client.SetToken(conf.VaultToken)
	/*
		ctx, err := WriteSecret(err, client)
		if err != nil {
			log.Println("Secret written successfully.")
			panic(err)
		}
	*/
	// Read a secret
	//secret, err := client.KVv2("secret").Get(ctx, "my-secret-password")
	ctx := context.Background()
	secret, err := client.KVv1("kv").Get(ctx, "wsf-secret-password")
	if err != nil {
		log.Fatalf("unable to read secret: %v", err)
	}

	return secret.Data
}

func WriteSecret(err error, client *vault.Client) (context.Context, error) {
	secretData := map[string]interface{}{
		"provisionUserName": "admin",
		"provisionPassword": "admin",
	}
	ctx := context.Background()
	// Write a secret
	//_, err = client.KVv2("secret").Put(ctx, "my-secret-password", secretData)
	err = client.KVv1("kv").Put(ctx, "wsf-secret-password", secretData)
	if err != nil {
		log.Fatalf("unable to write secret: %v", err)
	}

	log.Println("Secret written successfully.")
	return ctx, err
}
