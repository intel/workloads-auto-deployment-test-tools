/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
package main

import (
	config "api-provision/conf"
	"api-provision/routers"
	"context"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"github.com/gin-gonic/gin"
)

type RouterList []func(r *gin.Engine)

var routerList = RouterList{
	routers.AuthRouter,
	routers.ConfRouter,
	routers.FileRouter,
	routers.StatusMachineRouter,
}

func regRouters(r *gin.Engine) {
	for _, router := range routerList {
		router(r)
	}
}

func graceShutdown(r *gin.Engine, listenAddress string) {
	srv := &http.Server{
		Addr:           listenAddress,
		Handler:        r,
		ReadTimeout:    10 * time.Second,
		WriteTimeout:   10 * time.Second,
		MaxHeaderBytes: 1 << 20,
	}
	if config.Https {
		// https
		go func() {
			if err := srv.ListenAndServeTLS("./cert/cert.pem", "./cert/key.pem"); err != nil && err != http.ErrServerClosed {
				log.Fatalf("listen: %s\n", err)
			}
		}()
	} else {
		// http
		go func() {
			if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
				log.Fatalf("listen: %s\n", err)
			}
		}()
	}
	quit := make(chan os.Signal)
	signal.Notify(quit, os.Interrupt)
	<-quit
	log.Println("Shutdown Server ...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server Shutdown:", err)
	}
	log.Println("Server exiting")
}

func defaultLog(stdout bool) {
	f, _ := os.Create(config.LogPath)
	if stdout {
		gin.DefaultWriter = io.MultiWriter(f, os.Stdout)
	} else {
		gin.DefaultWriter = io.MultiWriter(f)
	}
}
