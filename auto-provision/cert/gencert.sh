#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

function genCert(){

	GOROOT=$(go env | grep GOROOT | awk -F'=' '{print $2}' | awk -F'"' '{print $2}')
	GOFILE="$GOROOT/src/crypto/tls/generate_cert.go"
	read -p "Enter the server communication IP to generate cert:" IPADDRESS
        if [ -f "$GOFILE" ]; then
		go run "$GOFILE" -host="$IPADDRESS" -ecdsa-curve="P384"
	else
		chmod +x generate_cert
		./"generate_cert" -host="$IPADDRESS" -ecdsa-curve="P384"
	fi
} 

genCert

if [ $? -eq 0 ]; then
	echo "generate cert succeed"
else
	echo "generate cert failed"
	exit 1
fi
