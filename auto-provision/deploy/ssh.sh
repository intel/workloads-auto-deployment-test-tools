#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#


function printLine() {
	if [ ! $1 ]; then
		outword='='
	else
		outword=$1
	fi
	shellwidth=$(stty size | awk '{print $2}')
	yes $outword | sed $shellwidth'q' | tr -d '\n'
}

function ssh () {
	cd "./ssh"
	gum confirm "Do you want to configure SSH password free?" \
		&& echo "example:" \
		&& echo "ip 	      hostname 			user password" \
		&& printLine \
		&& cat "./example.txt" \
		&& printLine
	gum write --placeholder "ip hostname user password (CTRL+D to finish)" > "host.conf"
	result=$(cat host.conf | awk '{if(length !=0) print $0}')
	echo "$result" > "host.conf"
	#./ssh_login.sh
	cd -
}

ssh

