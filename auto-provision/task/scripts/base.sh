#!/usr/bin/env bash

proxyCommand='nc -x child-prc.intel.com:1080 %h %p'

function checkArgEmpty() {
	if [ ! -n "$1" ]; then
		echo "IS NULL"
	else
		echo "NOT NULL"
	fi
}

function getAllFilesInDirectory() {
	for file in $(ls -a $1); do
		if [ -d $1"/"$file ]; then
			if [[ $file != '.' && $file != '..' ]]; then
				getAllFilesInDirectory $1"/"$file
			fi
		else
			echo $1"/"$file
		fi
	done
}

function printLine() {
	if [ ! $1 ]; then
		outword='='
	else
		outword=$1
	fi
	shellwidth=$(stty size | awk '{print $2}')
	yes $outword | sed $shellwidth'q' | tr -d '\n'
}

function containsStr() {
	if [[ $1 =~ $2 ]]; then
		return 0
	else
		return 1
	fi
}

function echoColor() {
	case $1 in
	green)
		echo -e "\033[32;40m$2\033[0m"
		;;
	red)
		echo -e "\033[31;40m$2\033[0m"
		;;
	*)
		echo "Example: echo_color red string"
		;;
	esac
}

function rootAuth() {
	if [ $UID -ne 0 ]; then
		echoColor red "Non root user. Please run as root."
		exit 1
	else
		echoColor green "Root user"
	fi
}

function systemType() {
	if [ -f /etc/redhat-release ]; then
		echo "CentOS"
	elif [ -f /etc/lsb-release ]; then
		echo "Ubuntu"
	else
		echo "Unknown"
		exit 1
	fi
}

function execScript() {
	# $1: script absolute path $2 cmd args
	cd $(dirname $1)
	suffixFlag=$(echo $(basename $1) | awk -F "." '{print $2}')
	if [ $suffixFlag == "py" ]; then
		python3 ./$(basename $1) $2
	else
		./$(basename $1) "$2"
		cd -
	fi
}

function log() {
	echo -e "$(date "+%Y-%m-%d %H:%M:%S") ${2}\n${3}" >>${1}
}

function waitHostRestart() {
	echo "Waiting for restart......"
	sleep 12
	while true; do
		if ping -c 1 $1 >/dev/null; then
			echo "$1 OK."
			echo done!
			break
		else
			echo "$1 NO! "
			echo "Waiting for restart......"
			sleep 10s
		fi
	done
}
