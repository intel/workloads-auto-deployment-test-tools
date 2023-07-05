#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#


function clearDir () {

	if [ -d "$1" ]; then
		rm -rf "$1"
	fi
}

function clearFile () {
	
	if [ -f "$1" ]; then
		rm -rf "$1"
	fi
}


function clearRoles () {
	
	local prefixRoles="../task/ansible/roles/"
	local roles=$(ls "$prefixRoles")
	for role in ${roles[@]}
	do
		:> "$prefixRoles/${role}/vars/main.yml"
		:> "$prefixRoles/${role}/files/workload.sh"
		:> "$prefixRoles/${role}/files/base_function.sh"
	done
}

function run () {

	#clear log
	clearDir "../output"
	#clear cert
	clearFile "../cert/cert.pem"
	clearFile "../cert/key.pem"
	#clear jenkins
	clearFile "../task/jenkins/getSecret"
	#clear air
	clearDir "../tmp"
	clearRoles

}

run
if [ $? -eq 0 ]; then
	echo "clear succeed"
else
	echo "clear failed"
	exit 1
fi
