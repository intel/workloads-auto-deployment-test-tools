#!/bin/bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

rm -rf /root/.ssh/id_rsa*
ssh-keygen -f /root/.ssh/id_rsa -t rsa -N ''
chmod +x ./ssh_copy_id.expect

cat ./host.conf | while read line; do
        echo ${line}
        ipAddr=$(echo $line | awk '{print $1}')
        hostname=$(echo $line | awk '{print $2}')
	echo $hostname
        user=$(echo $line | awk '{print $3}')
        password=$(echo $line | awk '{print $4}')
        ipFlag=$(echo $ipAddr | awk -F"." '{print $1}')
        if [ $ipFlag == 10 ]; then
                # intel server
                #./ssh_copy_id.expect $ipAddr $hostname $user $password
                ./ssh_copy_id.expect $ipAddr $ipAddr $user $password
                #sshpass -p "$password" ssh-copy-id "$user@$ipAddr"
                #sshpass -p "$password" ssh-copy-id "$user@$hostname"
        else
                # other cloud platforms
                sshpass -p "$password" ssh-copy-id -o ProxyCommand='nc -x child-prc.intel.com:1080 %h %p' "$user@$ipAddr"
        fi

done
