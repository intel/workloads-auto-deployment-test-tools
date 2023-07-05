#!/usr/bin/env bash 
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

source "../../collection/configs/$1"
source "../../lib/base_function.sh"
function updateBios() {
	# update config
	echo "start update bios......"
	biosConfigPath="../bios_setup/libs/recommendBios/cyp_bios.sh"
	: > biosConfigPath
	for item in "${biosArgs[@]}"
	do
		echo $item >> $biosConfigPath
	done

	cd "../bios_setup/installation/bios_commercial"
	if [ -f /etc/redhat-release ]; then
		echo "SLES"
		#./install_for_commercial_board.sh SLES 
		./update_bios.expect SLES
	elif [ -f /etc/lsb-release ]; then
		echo "UBUNTU"
		#./install_for_commercial_board.sh UBUNTU
		./update_bios.expect UBUNTU
	else
		echo "Unknown"
		exit 1
	fi
	
}

updateBios
 
