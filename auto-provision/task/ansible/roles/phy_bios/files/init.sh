#!/usr/bin/env bash

REPOTOKEN="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"
XMLCLIREPO="github.com/intel-innersource/applications.validation.platform-automation.xmlcli.xmlcli"
BIOSMANAGERREPO="github.com/intel-sandbox/BIOSManager.git"
function Init() {
	BIOSREPONAME="BIOSManager"
	XMLCLIREPONAME="xmlclirepo"
	if [ -d "$BIOSREPONAME" ];then
		rm -rf "$BIOSREPONAME"
	fi
	if [ -d "$XMLCLIREPONAME" ];then
		rm -rf "$XMLCLIREPONAME"
	fi
	git clone https://oauth2:"$REPOTOKEN"@"$BIOSMANAGERREPO"
	cd "$BIOSREPONAME"
	git switch auto_provision
	mkdir log
	cp "../runinconda.sh" "./"
	#pip3 install -r requirements.txt
	cd -
	source	"./workload.sh"
	echo "$biosArgs" > "./$BIOSREPONAME/config.yaml"

	git clone https://oauth2:"$REPOTOKEN"@"$XMLCLIREPO" "$XMLCLIREPONAME"
	cd "./$XMLCLIREPONAME"
	cp -r "./modules" "../$BIOSREPONAME"
	cp -r "./src" "../$BIOSREPONAME"

}

Init

