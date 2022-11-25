#!/usr/bin/env bash

install_depency(){
	if [ -f /etc/redhat-release ]; then
		sudo yum install -y jq
	else
		sudo apt-get install -y jq
	fi
}

add_proxy() {
	if [ ! -d "/etc/docker" ]; then
		mkdir /etc/docker
		sudo tee /etc/docker/daemon.json << EOF
{
  "exec-opts": [
    "native.cgroupdriver=systemd"
  ],
  "insecure-registries": [
    "https://r49s04.gv.intel.com:10443",
    "amr-registry.caas.intel.com",
    "dcsorepo.jf.intel.com",
    "r49s04.gv.intel.com",
    "vcaa-jf5-lab-1.jf.intel.com:10443",
    "10.219.170.195:5000",
    "10.67.121.79:5000",
    "10.166.44.56:5000",
    "{{registry}}"
  ],
  "experimental": true,
  "registry-mirrors": [
    "http://docker.mirrors.ustc.edu.cn",
    "http://hub-mirror.c.163.com"
  ]
}

EOF
else
	dockerDaemon="/etc/docker/daemon.json"
	registryStatus=$(cat $dockerDaemon | jq '."insecure-registries" | index( "{{registry}}" )')
	echo $registryStatus
	if [ $(echo $registryStatus) == "null" ]; then
		#jq '."insecure-registries"' $dockerDaemon
		jq --arg new "{{registry}}" '."insecure-registries"? += [$new]' $dockerDaemon > temp.json
		cat temp.json > $dockerDaemon
		cat $dockerDaemon
	fi

	fi
	ip=$(hostname -I)
	ipFlag=$(echo $ip | awk -F"." '{print $1}')
	if [[ $ipFlag == 10 ||  $ipFlag == 192 ]]; then
		echo "intel server"
		if [ ! -d "/root/.docker" ]; then
			mkdir ~/.docker
		fi
		sudo tee ~/.docker/config.json << EOF
{
  "proxies": {
    "default": {
      "httpProxy": "http://proxy-prc.intel.com:912",
      "httpsProxy": "http://proxy-prc.intel.com:912",
      "noProxy": "network-ai2,127.0.0.1,10.240.224.51,192.168.51.1,172.18.0.1,localhost,virt-api,.svc,.svc.cluster.local,cdi-api,127.0.0.1,10.96.0.0/12,10.32.0.0/12,10.32.0.0/12,172.32.1.0/12,localhost,virt-api,.svc,.svc.cluster.local,cdi-api,127.0.0.1,10.96.0.0/12,10.32.0.0/12,10.245.0.0/16,10.67.115.240,10.67.115.43,NONE"
}
}
}

EOF
# add systemd
if [ ! -d "/etc/systemd/system/docker.service.d" ]; then
	mkdir /etc/systemd/system/docker.service.d
fi
touch /etc/systemd/system/docker.service.d/http-proxy.conf
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf <<EOF
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2020 Intel Corporation

[Service]
Environment="HTTP_PROXY=http://child-prc.intel.com:913"
Environment="HTTPS_PROXY=http://child-prc.intel.com:913"
Environment="NO_PROXY=see-prc-renlefu-ci-pwek-server-1,127.0.0.1,10.240.224.51,192.168.51.1,172.18.0.1,localhost,virt-api,.svc,.svc.cluster.local,cdi-api,127.0.0.1,10.96.0.EOF
EOF

else
	echo "other cloud platforms......"
	fi
	sudo systemctl daemon-reload
	sudo systemctl restart docker
}

install_depency
add_proxy
