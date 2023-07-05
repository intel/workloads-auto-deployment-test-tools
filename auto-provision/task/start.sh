#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

configFileName="$1"
source "./conf/$configFileName.sh"
source "./scripts/base.sh"
source "./scripts/log.sh"
sshConfigFilePath="./ssh/host.conf"

# public method
function sendEmail() {
	# s1 message content $2 enclosure
	cd "./scripts"
	if [ ! -n "$2" ]; then
		python3 "./sendmail.py" "-s $sender -r $receivers -c "${1//" "/-}""
	else
		python3 "./sendmail.py" "-s $sender -r $receivers -c "${1//" "/-}" -f $2"
	fi
	cd -
}

function sshSecret() {
	: >"$sshConfigFilePath"
	for ((i = 1; i < ${#deployHost[@]}; i++)); do
		hostConf=$(echo ${deployHost[$i]} | awk -F"," '{print $3 " " $5 " " $4 " " $6}')
		echo $hostConf >>"$sshConfigFilePath"
	done
	cd "./ssh"
	./ssh_login.sh
	cd -
}

function configInsecureRegistry() {
    for ((i = 1; i < ${#deployHost[@]}; i++)); do
        ip=$(echo ${deployHost[$i]} | awk -F"," '{print $3}')
		user=$(echo ${deployHost[$i]} | awk -F"," '{print $4}')
		#copy script to remote server
		scp scripts/config_insecure_registry.sh $user@$ip:/tmp
		if [ "$user" == "root" ]
		then
		    ssh $user@$ip "cd /tmp;chmod +x config_insecure_registry.sh;./config_insecure_registry.sh $registry > /tmp/config_insecure_registry.out"
		else
		    ssh $user@$ip "cd /tmp;chmod +x config_insecure_registry.sh;sudo ./config_insecure_registry.sh $registry > /tmp/config_insecure_registry.out"
		fi
    done
}

function updateStatus() {
	# $1 progress $2 status
	echo "{"progress": $1}" | http put "$frontApi"
	echo "{"status": "$2"}" | http put "$frontApi"
}

function waitHostRestart() {
	# $1 ip address
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
			sleep 10
		fi
	done
}

function initDeploy() {
	#sshSecret
	cd "./ansible/"
	./init_roles.sh  $configFileName
	cd -
}

function kubernetesDeploy() {
	if [ $kubernetes_deploy == "true" ]; then
		if [ $kubernetesInstallMethod == "host" ]; then
			cd "./cluster"
			"./kubescray_host.sh" "$configFileName"
			cd -
		fi
		if [ $kubernetesInstallMethod == "docker" ]; then
			#TODO
			#cd "./ansible"
			#ansible-playbook docker_site.yaml
			:
		fi
		if [ $kubernetesInstallMethod == "vm" ]; then
			#TODO
			:
		fi
	fi
}

function systemDeploy() {
	if [ $system_deploy == "true" ]; then
		cd "./ansible"
		if [ $os_update == "true" ]; then
			#TODO
			echo "Operating system installation is not currently supported"
		fi
		if [ $Kernel_update == "true" ]; then
			ansible-playbook kernel_site.yaml
		fi
		if [ $kernelArgs_update == "true" ]; then
			ansible-playbook kernel_args_site.yaml
		fi
		if [ $bios_update == "true" ]; then
			#ansible-playbook bios_site.yaml -vv
			echo "update bios is not supported"
		fi
		cd -

		if [ "$Kernel_update" == "true" -o "$kernelArgs_update" == "true" -o "$bios_update" == "true" ]; then
			for ip_user in $(cat $sshConfigFilePath | awk -F" " '{print $1"->-"$3}'); do
				ip=$(echo "$ip_user" | awk -F"->-" '{print $1}')
				user=$(echo "$ip_user" | awk -F"->-" '{print $2}')
				#ssh "$user"@"$ip" "shutdown now"
			done
			for ip in $(cat $sshConfigFilePath | awk -F" " '{print $1}'); do
				#waitHostRestart $ip
				echo "check the machine......"
			done
		fi
	fi
}

function vmDeploy() {
	if [ $vm_deploy == "true" ]; then
		cd "./ansible"
		ansible-playbook virtualmachine_site.yaml
		cd -
	fi
}

function workloadDeploy() {
	if [ $jenkins == "true" ]; then
		#cd "./ansible"
		#ansible-playbook docker_site.yaml
		#cd -
		cd "./jenkins"
		./jenkins_api.sh $configFileName
		cd -
	fi

}

function softwarePackage() {
	if [ $softwarepackage == "true" ]; then
		cd "./ansible"
		ansible-playbook workload_site.yaml
		cd -
	fi

}

#feedback
function startTask() {
	initDeploy
	kubernetesDeploy
	systemDeploy
	#vmDeploy
	softwarePackage
	configInsecureRegistry
	workloadDeploy
}

startTask
