#!/usr/bin/env bash

#set -x

source "./base_function.sh"
source "./workload.sh"
printLine

echoColor green $kernelVersion
kernelHeaders=($(apt-cache search linux | grep headers | grep x86 | grep generic | awk -F" " '{print $1}' | grep $kernelVersion))
kernelVersion=$kernelVersion	
kernelHeader=${kernelHeaders[0]}
kernelImage="${kernelHeader/headers/image}"
echoColor green $kernelVersion
echoColor green $kernelHeader
echoColor green $kernelImage
echoColor green $kernelVersionAbs
printLine

function getSystemKernel() {
	system_kernel="$(uname -r)"
	echoColor green "The local kernel version is $system_kernel"
}

function getInstlledKernel() {
	echoColor green $(dpkg --get-selections | grep linux-image | grep -v deinstall)
}

function installKernel() {
	sudo apt-get install $kernelHeader -y
	sudo apt-get install $kernelImage -y
}

function updateGrub() {
	#GRUB_DEFAULT=0
	#Example GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux 5.11.0-25-generic"
	kernelVersionAbs=${kernelImage#linux-image-}
	echoColor green $kernelVersionAbs
	sed -i '/^GRUB_DEFAULT/cGRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux '$kernelVersionAbs'"' /etc/default/grub
	sudo update-grub
	#sudo reboot now

}

function run() {
	rootAuth
	getSystemKernel
	printLine
	getInstlledKernel
	installKernel
	printLine
	updateGrub
	printLine
}

run
