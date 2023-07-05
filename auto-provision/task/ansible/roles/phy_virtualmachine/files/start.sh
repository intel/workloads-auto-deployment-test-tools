#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

source "./workload.sh"

./install_kvm.sh
./install_kcli.sh
./create_vm.sh

osNumber=${vmosArgs["osNumber"]}
for i in $(seq $osNumber)
do
	while true; do
		getIp=$(kcli  info vm ${vmosArgs["vmName"]}${i} | grep ip:)
		echo $getIp
		if [[ "$getIp" != "" ]]
		then
			echo "ip exists"
			break
		else
			echo "ip not exists start gete ip......"
			sleep 1
		fi
	done
	kcli scp -r "./*" root@${vmosArgs["vmName"]}${i}:/root
	kcli ssh root@${vmosArgs["vmName"]}${i} "./config_proxy.sh"
	if [ "$vm_docker" == "true" ]; then
		kcli ssh root@${vmosArgs["vmName"]}${i} "./install_docker.sh"
		kcli ssh root@${vmosArgs["vmName"]}${i} "./config_docker_proxy.sh"
	fi
done

