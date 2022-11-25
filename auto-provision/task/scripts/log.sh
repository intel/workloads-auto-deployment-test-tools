#!/usr/bin/env bash

# Treat unset variables as an error
#set -o nounset

export GLOBAL_FAIL_FLAG="$(
	cd $(dirname ${BASH_SOURCE[0]})
	pwd
)/globalFailFlag.tag"

if [ "${1}" != "default" ]; then
	TAG_FOR_SHELL="${1} "
else
	TAG_FOR_SHELL=""
fi

function Show() {
	dateStr=$(echo $(date +%Y-%m-%d) $(date +[%H:%M:%S]))
	if [ ! -f ${GLOBAL_FAIL_FLAG} ]; then
		echo "${dateStr} ${TAG_FOR_SHELL}$@"
	fi
}

function BlankLine() {
	echo ""
}

function CleanShow() {
	echo "$@"
}

function Step() {
	sourceFileName=$(caller)
	Show ""
	Show "==================== ${sourceFileName##*/}  STEP $1 : $2 ===================="
	Show ""
}

function BeforeShell() {
	sourceFileName=$(caller)
	Show ""
	Show "   +   ${sourceFileName##*/}  BEGIN   +"
	Show "   +   ${sourceFileName##*/} $@   +"
	Show ""
}

function AfterShell() {
	sourceFileName=$(caller)
	Show ""
	Show "   +   ${sourceFileName##*/}  FINISH   +"
}

function ReportFailure() {
	touch ${GLOBAL_FAIL_FLAG}
	echo ""
	echo "****     line $(caller) REPORTED FAILURE     ****"
	echo ""
	echo "    CALLER LIST    "
	echo " - line $(caller 0)"
	for loop in 1 2 3 4; do
		if [ "$(caller ${loop})" != "" ]; then
			echo " - line $(caller ${loop})"
		else
			echo ""
			break
		fi
	done
}

function ReportSuccess() {
	echo ""
	echo "****     $1 SUCCESS      ****"
	echo ""
}

function CleanFailFlagBeforeStart() {
	if [ -f ${GLOBAL_FAIL_FLAG} ]; then
		rm -f ${GLOBAL_FAIL_FLAG}
	fi
}

: <<EOF
#source ./log.sh default
#source ./log.sh [packeriso]

CleanFailFlagBeforeStart

BeforeShell [start get jobId]
Step second "get a jobid"
Show "Hello World"
Show "Using TAG to LOG"
Show "This is a demo for shell"
AfterShell

ReportSuccess "Build Dynamic Framework Project"	
ReportFailure
EOF
