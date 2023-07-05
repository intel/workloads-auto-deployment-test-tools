#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

source "./base_function.sh"
source "./workload.sh"

# Ubuntu CentOS
# CentOS 恢复默认修改参数 grubby --update-kernel=DEFAULT --remove-args "intel_iommu=on iommu=pt"
# Ubuntu 恢复默认修改参数 GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"

#system=Ubuntu
system=$(systemType)
args=$kernelArgs
#args='\"intel_iommu=on iommu=pt\"'

function set_Kernel_command_line(){
    if [ "Ubuntu" == $system ]; then
        n_line=$(grep '^GRUB_CMDLINE_LINUX_DEFAULT=' -n /etc/default/grub | cut -d ':' -f 1)
        sed -i 's/^GRUB_CMDLINE_LINUX_DEFAULT=/#GRUB_CMDLINE_LINUX_DEFAULT=/' /etc/default/grub
        sed -i "${n_line}i GRUB_CMDLINE_LINUX_DEFAULT=$args" /etc/default/grub
        sudo update-grub
    elif [ "CentOS" == $system ]; then
        echo "CentOS"
        sudo grubby --update-kernel='DEFAULT' --args=$args
    else
        sudo grubby --update-kernel='DEFAULT' --args=$args
        #echo "[error]: System is not Ubuntu or CentOS; Failed to set grubby "
        #exit 1
    fi
}

#check_system
set_Kernel_command_line
