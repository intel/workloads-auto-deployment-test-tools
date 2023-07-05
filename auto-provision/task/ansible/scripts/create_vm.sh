#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

set -x
#source ../../collection/configs/sf_qatcpa.sh
source ../../collection/configs/$1
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
	echo ${vmosArgs["osNumber"]}
	echo ${vmosArgs["osType"]}
	echo ${vmosArgs["vmName"]}
	echo ${vmosArgs["memory"]}
	echo ${vmosArgs["cpuNumber"]}
	echo ${vmosArgs["disk"]}
	# centos7 centos8 ubuntu1804 ubuntu 2004
	# $1 osName $2 vmName  $3 disk size
	initVM
	kcli download image ${vmosArgs["osType"]}
	# kcli create vm -i $1 $2
	for i in $(seq "${vmosArgs["osNumber"]}")
	do
		kcli create vm ${vmosArgs["vmName"]}${i} -i ${vmosArgs["osType"]} -P disks=["{"\"size"\":${vmosArgs["disk"]} , "\"interface"\": "\"sata"\"}"] -P memory=${vmosArgs["memory"]} -P numcpus=${vmosArgs["cpuNumber"]}
	done
	kcli list vm
	# wait 5-10 seconds for vm to grab an ip
}

function configVM(){
	# kcli ssh myvm
	# kcli delete vm
	# kcli clone -b myvm -f -s myvm
	# kcli update vm -P numcpus=8 myvm
	# kcli update vm -P memory=2048 myvm
	# kcli update vm -P ip=192.168.122.111 myvm  cant't connect ssh
	# kcli create vm-disk -s 20 -p default myvm2
	initVM
	installVM
	kcli stop vm ${vmosArgs["vmName"]}
	# diskSize=`expr ${vmosArgs["disk"]} - 10`
	for i in $(seq `expr "${vmosArgs["osNumber"]}" - 1`)
	do
		#kcli clone -b ${vmosArgs["vmName"]} -f -s ${vmosArgs["vmName"]}${i}
		#virt-clone -o  ${vmosArgs["vmName"]} --auto-clone
		#installVM ${vmosArgs["osType"]} ${vmosArgs["vmName"]}${i}
		kcli create vm ${vmosArgs["vmName"]}${i} -i ${vmosArgs["osType"]} -P disks=["{"\"size"\":${vmosArgs["disk"]} , "\"interface"\": "\"sata"\"}"] -P memory=${vmosArgs["memory"]} -P numcpus=${vmosArgs["cpuNumber"]}
		kcli stop vm ${vmosArgs["vmName"]}${i}
		sleep 8
		#kcli update vm -P numcpus=${vmosArgs["cpuNumber"]}  ${vmosArgs["vmName"]}${i}
		#kcli update vm -P memory=${vmosArgs["memory"]} ${vmosArgs["vmName"]}${i}
		#kcli create vm-disk -s $diskSize -p default ${vmosArgs["vmName"]}${i}
		#config network get IP
		#kcli start vm ${vmosArgs["vmName"]}${i}
	done
	#kcli start vm ${vmosArgs["vmName"]}


}

#installVM "centos7" "myvm3"
#installVM "centos8" "centos814"
#installVM "ubuntu2004" "ubuntu20042"

#for key in ${!vmosArgs[@]}
#do
#echo ${vmosArgs[$key]}
#done


#for i in $(seq `expr "${vmosArgs["osNumber"]}" - 1`)
#do
#echo ${vmosArgs["vmName"]}${i}
#done
#diskSize=`expr ${vmosArgs["disk"]} - 10`
#echo $diskSize

#configVM
installVM













