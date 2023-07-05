#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

source "./base_function.sh"
source "./workload.sh"

function start() {
	for((i=1; i < "${#softwarepackageArgs[@]}" ; i++)); do
		packageName=$(echo "${softwarepackageArgs[$i]}" | awk -F ',' '{print $1}')
		packageArgs=$(echo "${softwarepackageArgs[$i]}" | awk -F ',' '{print $2}')
		#echo "$packageName"
		#echo "$packageArgs"
		if [ ! -d "./workload-packages/"$packageName"" ]; then
			echo "[error:the workloadpackage not exists]"
			exit 1;
		fi
		cd "./workload-packages/"$packageName""
		filelist=$(find ./)
		for file in $(echo $filelist); do
			sudo chmod +x "$file"
		done
		#echo "Password123" | sudo -S ./start.sh "$packages"
		./start.sh "$packages"
		echo "hello,dpdk~"
		cd -
	done
}

start

