#!/usr/bin/env bash

#set -x

function tools () {

	cd ../tools
	for tool in $(ls)
	do
		if ! command -v $tool >/dev/null 2>&1; then
			cp $tool /usr/bin/
		else
			echo "$tool installed"
		fi
	done
	cd -
}

tools
