#!/usr/bin/env bash
# usage
# echo {{password}} | sudo -S ./{{script_name}}

#set -x
# system package
soft_name_all=("tcl" "expect" "jq")


function installSoft() {

	if [ -f /etc/redhat-release ]; then
		sudo yum install -y "$1"
	else
		sudo apt-get install -y "$1"
	fi
}

function createDir() {

	local logPath="../output/log/"
	if [ ! -d "$logPath" ]; then
		mkdir -p "$logPath"
	fi
        local confPath="../task/conf"
        if [ ! -d "$confPath" ]; then
                mkdir -p "$confPath"
        fi
}

function installVault () {
			
        if ! command -v vault >/dev/null 2>&1; then
                echo "start install vault......"
		if [ -f /etc/redhat-release ]; then
		     sudo yum install -y yum-utils
		     sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
		     sudo yum -y install vault
		else
		     sudo apt update && sudo apt install gpg
		     wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | \
		     sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg >/dev/null
		     gpg --no-default-keyring \
		     --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint
		     echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com \
		     $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
		     sudo apt update && sudo apt install vault
		fi
        else
                echo "vault is installed."
        fi


}

function installHttpie () {

        if ! command -v http >/dev/null 2>&1; then
                echo "start install httpie......"
                if [ -f /etc/redhat-release ]; then
                        yum install epel-release
                        yum install httpie
                else
                        curl -SsL https://packages.httpie.io/deb/KEY.gpg | apt-key add -
                        curl -SsL -o /etc/apt/sources.list.d/httpie.list https://packages.httpie.io/deb/httpie.list
                        apt update
                        apt install httpie
                fi
        else
                echo "httpie is installed."
        fi

}

function getSecret(){
	go build getSecret.go		
	mv ./getSecret ../task/jenkins/	
}

function run() {

	installVault
	installHttpie
	getSecret
	# system package
	for soft_name in "${soft_name_all[@]}"; do
		echo "Installing${soft_name}......"
		installSoft "$soft_name"
	done
	#pip3 install -r ./requirements.txt
	# create log dir
	createDir

	# https cert
	cd "../cert"
	./gencert.sh
	rm -f ../../portal/backend/cert/*.pem;cp *.pem ../../portal/backend/cert
	rm -f /home/*.pem;cp *.pem /home
	cd -

}

run

if [ $? -eq 0 ]; then
	echo "install package succeed"
else
	echo "install package failed"
	exit 1
fi
	
