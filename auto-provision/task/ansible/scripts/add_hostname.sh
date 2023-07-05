#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#


function addAWordInEveryLine(){
	# $1 word $2 filename
	if [ -n "$1" ]; then
		sed -i "s/$/& $hostName/g" "$2"
	else
		echo "word is null"
	fi

}

function changeHosts(){

	local hostName=$(hostname)
	local fileName="/etc/hosts"
	for word in $(awk 'NF>1{print $NF}' "$fileName");do
		echo $word
		echo $hostName
		if [ "$word" == "$hostName" ]; then
			echo "hostname has been added......"
		else
			sed -i '/^$/d' "$fileName"
			addAWordInEveryLine $word "$fileName"
			break
		fi
	done

}

changeHosts

