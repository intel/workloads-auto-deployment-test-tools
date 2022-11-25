#!/usr/bin/env bash

CENTOS7_vm="https://cloud.centos.org/centos/7/images/CentOS-7-aarch64-GenericCloud-2009.qcow2"
CENTOS8_vm="https://cloud.centos.org/centos/8-stream/x86_64/images/CentOS-Stream-GenericCloud-8-20210603.0.x86_64.qcow2"
UBUNTU1804_VM="https://cloud-images.ubuntu.com/releases/bionic/release-20220104/ubuntu-18.04-server-cloudimg-amd64.img"
UBUNTU2004_VM="https://cloud-images.ubuntu.com/releases/focal/release-20220111/ubuntu-20.04-server-cloudimg-amd64-disk-kvm.img"


function downloadVMISO(){

	if [ $1 == "centos7" ]; then
		wget -O centos7.qcow2 $CENTOS7_VM
	elif [ $1 == "centos8" ]; then
		wget -O centos8.qcow2 $CENTOS8_VM
	elif [ $1 == "ubuntu1804" ]; then
		wget -O ubuntu1804.img $UBUNTU1804_VM
	elif [ $1 == "ubuntu2004" ]; then
		wget -O ubuntu2004.img $UBUNTU2004_VM
	fi
	mv *.qcow2 /tmp
	mv *.img /tmp
}


function strContain(){
    local str=$1
    local subStr=$2
    if [[ ${str} =~ ${subStr} ]];then
	echo "true"
    else
	echo "false"
    fi
}

function createbridge(){

	 #virsh net-define bridge.xml
	 #virsh net-start bridge
	 #virsh net-autostart bridge
	 # get network
        local cardList=$(ifconfig | grep -E '^[a-zA-Z0-9]+' | awk '{print $1}' | awk -F':' '{print $1}')
        echo $cardList
        for card in $cardList:
        do
                echo $card
                if [ $(strContain "$card" "eno") == "true" -o $(strContain "$card" "ens" ) == "true" -o $(strContain "$card" "eth") == "true" ];th                        echo "true"
			virsh iface-bridge $card br0
                        break
                fi
        done
}

function installMV(){

	# check file exist
	image=$(echo "${vmosArgs["disk"]}" | awk -F "," '{print $1}' | awk -F "=" '{print $2}')
	if [ ! -f $image ]; then
		downloadVMISO "${vmosArgs["os"]}"
	fi
	# virsh iface-bridge eth1 br0
	virt-install --name "${vmosArgs["os"]}" \
		--ram "${vmosArgs["ram"]}" \
		--vcpus "${vmosArgs["vcpus"]}" \
		--os-variant rhel7\
		--disk "${vmosArgs["disk"]}",format=qcow2,bus=virtio\
		--network bridge=virbr0,model=virtio \
		--graphics vnc,port=-1\
		--noautoconsole --import
}

installMV
#virt-install --name centos7 --ram 4048 --vcpus=4 --disk path=CentOS-7-aarch64-GenericCloud-2111.qcow2,bus=ide,format=qcow2  --network=bridge:br0 --force --import  --autostart
