#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

#set -x
rm -rf kubespray
git clone -b master https://github.com/kubernetes-sigs/kubespray.git

if [ $? -eq 0 ]; then
	echo "download kubespray succeed"
else
	echo "download kubespray  failed"
	exit 1
fi
cd "./kubespray"
git reset --hard e6976a54e151b43483c89a5054f87a60007f4485
pip3 install -r requirements.txt
cd -
