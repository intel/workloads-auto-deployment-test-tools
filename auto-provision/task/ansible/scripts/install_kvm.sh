#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
set -x
function judgeUbuntuCentOS(){
    local release
    if [[ -f /etc/redhat-release ]]; then
        release="centos"
    elif cat /etc/issue | grep -Eqi "ubuntu"; then
        release="ubuntu"
    else
        echo "Unsupported operating system!"
        exit 1
    fi
    echo $release

}
function installKvm(){
    # check whether the host supports virtualization
    vmxsvm=$(grep -E '(svm|vmx)' /proc/cpuinfo)
    if [ -z $vmxsvm ];then
        echo "the cup is not support kvm"
        exit 1
    fi

    # install kvm
    if [ $(judgeUbuntuCentOS) == "centos" ]; then
        #yum install -y qemu-kvm libvirt libvirt-python libvirt-client bridge-utils
        #sudo yum update
        sudo yum install @virt
        sudo dnf -y install libvirt-devel virt-top libguestfs-tools python3-devel qemu-kvm libvirt
    else
        sudo apt -y install bridge-utils cpu-checker libvirt-clients libvirt-daemon qemu qemu-kvm python3-dev
        sudo apt -y install  libvirt-daemon-system  virtinst virt-manager


    fi

    checkResult=$(lsmod | grep kvm_intel | awk '{print $1}')
    loadResult=$(echo $checkResult | grep "kvm_intel")
    if [[ "$loadResult" != "" ]]
    then
	    echo "laod kvm module"
    else
	    echo "not load kvm module"
	    exit 1

    fi

    # check kvm acceleration
     #kvmok=$(kvm-ok | grep "KVM acceleration can be used")
     #if [ -z $kvmok ];then
         #echo "Your CPU does not support KVM extensions"
         #exit 1
     #fi

    # kvm group
    sudo usermod -aG libvirt $USER
    sudo usermod -aG kvm $USER
    sudo systemctl enable --now libvirtd

}

installKvm
