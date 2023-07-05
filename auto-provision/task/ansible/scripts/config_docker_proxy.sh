#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#


add_proxy() {
	mkdir /etc/docker
	echo '{ "registry-mirrors": ["https://fxkees7l.mirror.aliyuncs.com"] }' > /etc/docker/daemon.json
	ip=$(hostname -I)
	ipFlag=$(echo $ip | awk -F"." '{print $1}')
	if [[ $ipFlag == 10 ||  $ipFlag == 192 ]]; then
		echo "intel server"
		mkdir ~/.docker
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
        mkdir /etc/systemd/system/docker.service.d
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

add_proxy
