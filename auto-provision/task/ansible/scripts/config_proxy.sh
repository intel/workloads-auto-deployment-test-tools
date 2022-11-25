#!/usr/bin/env bash

#set -o nounset

#export PATH=$PATH:/root/.local/bin

proxy="http://child-prc.intel.com:912"
no_proxy=127.0.0.1,10.240.224.51,192.168.51.1,172.18.0.1,localhost,virt-api,.svc,.svc.cluster.local,cdi-api,127.0.0.1,10.96.0.0/12,10.32.0.0/12,10.32.0.0/12,172.32.1.0/12,localhost,virt-api,.svc,.svc.cluster.local,cdi-api,127.0.0.1,10.96.0.0/12,10.32.0.0/12,10.245.0.0/16,10.67.115.240,10.67.119.5:None

httpHttpsProxyFiles=("/etc/profile" "/etc/environment")
aptProxyFile="/etc/apt/apt.conf.d/proxy.conf"

function checkStr(){
        # check str in file
        # $1: file
        # $2: str
        if [ -f $1 ]; then
                if grep -q "$2" $1; then
                        echo "true"
                else
                        echo "false"
                fi
        else
                echo "this is not a file"
		exit 1
        fi

}

function getOSType(){
        # check the machine is ubuntu or centos
        if [ -f /etc/redhat-release ]; then
                echo "centos"
        elif [ -f /etc/lsb-release ]; then
                echo "ubuntu"
        else
                echo "the script not support other linux system now"
		exit 1
        fi
}

osType=$(getOSType)
result=$(checkStr "${httpHttpsProxyFiles[0]}" "http://child-prc.intel.com")
function addProxy() {

	if [ $result == "true" ]; then
		echo "http_proxy and https_proxy already configured...... "
	else
		for file in "${httpHttpsProxyFiles[@]}"; do
			echo "Start adding network agent......"
			echo "export http_proxy=${proxy}" >>$file
			echo "export https_proxy=${proxy}" >>$file
			echo "export no_proxy=${no_proxy}" >>$file
			source $file

		done
		if [ $osType == "ubuntu" ]; then
			echo "Acquire::http::Proxy \"${proxy}\";" >>$aptProxyFile
			echo "Acquire::https::Proxy \"${proxy}\";" >>$aptProxyFile
			source $aptProxyFile
		else
			echo "export proxy=${proxy}" >> /etc/yum.conf && yum makecache
		fi
	fi

}

addProxy
