#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

source "../../lib/base_function.sh"
source ../../collection/configs/$1
#source "../../collection/configs/sf_qatcpa.sh"

function updateKernelAndBios() {
	if [ $os_update == "true" ];then
		echo "installing operating system......"
		exit 1
	fi
	if [ $bios_update == "true" ]; then
		echo "update bios......"
		./update_bios.sh $1
	fi
	if [ $Kernel_update == "true" ]; then
		#./update_kernel.sh
		echo "update kernel"
	fi
	if [ "$kernelArgs_update" == "true" ]; then
		echo "update kernelArgs"
		./update_kernelArgs.sh $kernelArgs

	fi

}
#echo  $kernelArgs
#updateKernelAndBios
