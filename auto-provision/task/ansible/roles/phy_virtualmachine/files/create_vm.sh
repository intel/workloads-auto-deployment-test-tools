#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

set -x
source "./workload.sh"
function initVM() {
	# create config
	kcli create host kvm -H 127.0.0.1 local
	kcli create host kvm -H 192.168.0.6 host1
	# create storage pool
	sudo kcli create pool -p /var/lib/libvirt/images default
	sudo setfacl -m u:$(id -un):rwx /var/lib/libvirt/images
	# create network
	kcli create network -c 192.168.122.0/24 default
}

function installVM() {
	# centos7 centos8 ubuntu1804 ubuntu 2004
	echo ${vmosArgs["osNumber"]}
	echo ${vmosArgs["osType"]}
	echo ${vmosArgs["vmName"]}
	echo ${vmosArgs["memory"]}
	echo ${vmosArgs["cpuNumber"]}
	echo ${vmosArgs["disk"]}
	initVM
	kcli download image ${vmosArgs["osType"]}
	for i in $(seq "${vmosArgs["osNumber"]}")
	do
		kcli create vm ${vmosArgs["vmName"]}${i} -i ${vmosArgs["osType"]} -P disks=["{"\"size"\":${vmosArgs["disk"]} , "\"interface"\": "\"sata"\"}"] -P memory=${vmosArgs["memory"]} -P numcpus=${vmosArgs["cpuNumber"]}
	done
	kcli list vm
	# wait 5-10 seconds for vm to grab an ip
}

function configVM(){
	initVM
	installVM
	kcli stop vm ${vmosArgs["vmName"]}
	# diskSize=`expr ${vmosArgs["disk"]} - 10`
	for i in $(seq `expr "${vmosArgs["osNumber"]}" - 1`)
	do
		kcli create vm ${vmosArgs["vmName"]}${i} -i ${vmosArgs["osType"]} -P disks=["{"\"size"\":${vmosArgs["disk"]} , "\"interface"\": "\"sata"\"}"] -P memory=${vmosArgs["memory"]} -P numcpus=${vmosArgs["cpuNumber"]}
		kcli stop vm ${vmosArgs["vmName"]}${i}
		sleep 8
	done
	#kcli start vm ${vmosArgs["vmName"]}


}

#configVM
installVM













