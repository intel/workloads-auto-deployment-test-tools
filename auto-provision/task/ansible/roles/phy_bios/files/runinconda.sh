#!/usr/bin/env bash

set -x

ENVNAME="bios"
REQUIREMENTSFILE="requirements.txt"
#./run.sh --set <Path to Config yaml> [-nc/--no-create] [-rd/--restore-default]
EXECCMD='./run.sh --set "config.yaml"'


USER=$(whoami)
#USER="xianglingyu"
#INSTALLDIR="/$USER/miniconda"
INSTALLDIR="/miniconda"
BASHRC="/$USER/.bashrc"
if [ "$USER" != "root" ]; then
	INSTALLDIR="/home$INSTALLDIR"
	BASHRC="/home$BASHRC"
fi

MINICONDAPATH="$INSTALLDIR/bin/activate"

function InstallMiniconda () {
	local SCRIPTNAME="Miniconda_Install.sh"
	local DOWNLOADURL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"  
	wget --output-document "$SCRIPTNAME" "$DOWNLOADURL"
	bash Miniconda_Install.sh -b -f -p "$INSTALLDIR" 
	cd "$INSTALLDIR/bin"
	./conda init
	cd -
	source "$BASHRC"
	echo "$BASHRC"
}

function CreateEnv () {
	source "$MINICONDAPATH"
	conda create --name "$ENVNAME" -y
	source "$MINICONDAPATH"
	conda activate "$ENVNAME"
	source "$MINICONDAPATH"
	#createStatus=$(conda info --envs | awk -F' ' '{print $1}' | grep "$ENVNAME")
	pip3 install -r "$REQUIREMENTSFILE"
	pip3 list > result.txt
	echo "create env successed"	
	python --version
	eval "$EXECCMD"
}

function CheckEnv () {
	#source "$MINICONDAPATH"
        if ! command -v conda >/dev/null 2>&1; then                  
                echo "start install miniconda......"               
		InstallMiniconda
        fi    
}                 

CheckEnv
CreateEnv
