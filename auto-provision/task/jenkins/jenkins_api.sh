#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
# set -x
# example ./jenkins_api.sh 106-workload
configFileName="$1".sh
source "../conf/$configFileName"
source "../scripts/base.sh"
source "../scripts/log.sh"
source "../config.sh"

jenkinsUserName=$(./getSecret | grep "jenkinsUserName::" | awk -F':: ' '{print $2}')
jenkinsToken=$(./getSecret | grep "jenkinsToken::" | awk -F':: ' '{print $2}')
USER="$jenkinsUserName:$jenkinsToken"
portalUserName=$(./getSecret | grep "portalUserName::" | awk -F':: ' '{print $2}')
portalPassword=$(./getSecret | grep "portalPassword::" | awk -F':: ' '{print $2}')
smtpServer=$(./getSecret | grep "SMTPServer::" | awk -F':: ' '{print $2}')
smtpPort=$(./getSecret | grep "SMTPPort::" | awk -F':: ' '{print $2}')
JfrogUrl=$(./getSecret | grep "JfrogUrl::" | awk -F':: ' '{print $2}')
#BASEURL="https://workload-automation-dev1.jenkins.pact.intel.com"
BASEURL=$(./getSecret | grep "jenkinsUrl::" | awk -F':: ' '{print $2}')
#FRONTAPI="http://10.67.121.100:8899/local/api/job/$jobId/"
#FRONTURL="https://IP:PORT"
FRONTURL=$(./getSecret | grep "statusUrl::" | awk -F':: ' '{print $2}')
STATUS_API="${FRONTURL}/local/api/job/$jobId/"
INSTANCE_API="${FRONTURL}/local/api/instance/"
TESTRESULT_API="${FRONTURL}/local/api/test_result/"
function sendEmail() {
    # s1 message content $2 enclosure
    cd ../scripts
    if [ ! -n "$2" ]; then
        python3 sendmail.py -s $sender -r $receivers -c "${1//" "/===}" -m $smtpServer -p $smtpPort
    else
        python3 sendmail.py -s $sender -r $receivers -c "${1//" "/===}" -m $smtpServer -p $smtpPort -f $2
    fi
    cd -
}

function clearLocalMediaFile() {
    rm ../../../portal/backend/workspace/local/media/*
}


CleanFailFlagBeforeStart
BeforeShell [START jENKINS]
declare -a IPS=()
for ((i = 1; i < ${#deployHost[@]}; i++)); do
    ip=$(echo ${deployHost[$i]} | awk -F"," '{print $3}')
    IPS[$i]="$ip"
done

setArrayIp=($(awk -v RS=' ' '!a[$1]++' <<< ${IPS[@]}))
limited_node_number="${#setArrayIp[@]}"

CONTROLLER_IP=${IPS[1]}
unset IPS[1]
WORKER_IP_LIST=$(echo ${IPS[@]} | tr " " ",")
Show $CONTROLLER_IP
Show $WORKER_IP_LIST

#Create a new Jenkins job
Step first "CREATE A NEW JENKINS JOB" 
queuedId=$(curl -i \
    $BASEURL/job/full_benchmark/buildWithParameters/ \
    --user $USER \
    --data front_job_id=$jobId \
    --data platforms=$platforms \
    --data workload_list=$workloadName \
    --data controller_ip=$CONTROLLER_IP \
    --data repo=$jsfRepo \
    --data instance_api=$INSTANCE_API \
    --data django_execution_result_url=$TESTRESULT_API \
    --data artifactory_url=$JfrogUrl \
    --data sf_commit=$commit \
    --data registry=$registry \
    --data filter_case="$filterCase" \
    --data workload_params="$workloadParameter" \
    --data limited_node_number=$limited_node_number \
    --data worker_ip_list=$WORKER_IP_LIST | grep -i location | awk -F '/' '{print $6}')

Show $queuedId

#Get the really Job id to use
Step second "GET THE REALLY JOB ID TO USE"
result=(curl --user $USER $BASEURL/queue/item/$queuedId/api/json)
echo "$result" > "data.json"
while :; do
    jenkinsJobId=$(curl --user $USER $BASEURL/queue/item/$queuedId/api/json | jq '.executable.number')
    # TODO set timeout
    if [ $(echo $jenkinsJobId) != "null" ]; then
        Show "$jenkinsJobId"
        break
    fi
    Show "wait for the task to start......"
    sleep 5
done

# --auth USER[:PASS], -a USER[:PASS]
# --auth-type {basic, digest} Defaults to "basic"
HTTP_PUT_CMD="http put $STATUS_API --auth $portalUserName:$portalPassword --verify=no"

#Get Jenkins job status
Step third "GET JENKINS JOB STATUS"
Show "jenkinsStatus -->[running]"
echo '{"progress": 50}' | $HTTP_PUT_CMD
echo '{"status": "RUNNING"}' | $HTTP_PUT_CMD
while :; do
    jenkinsStatus=$(curl --user $USER \
        $BASEURL/job/full_benchmark/$jenkinsJobId/api/json | jq '.result')
    if [ $(echo $jenkinsStatus) == "null" ]; then
	Show "jenkinsStatus --> running"
	sleep 30
        continue
    fi
    if [ $(echo $jenkinsStatus) == '"FAILURE"' ]; then
        Show "jenkinsStatus -->[FAILURE]"
        echo '{"progress": 100}' | $HTTP_PUT_CMD
        echo '{"status": "JENKINS_FAILED"}' | $HTTP_PUT_CMD
        break
    fi
    if [ $(echo $jenkinsStatus) == '"ABORTED"' ]; then
        Show "jenkinsStatus -->[ABORTED]"
        echo '{"progress": 100}' | $HTTP_PUT_CMD
        echo '{"status": "JENKINS_ABORTED"}' | $HTTP_PUT_CMD
        break
    fi
    if [ $jenkinsStatus == '"SUCCESS"' ]; then
        Show "the task is already finished"
        echo '{"progress": 100}' | $HTTP_PUT_CMD
        echo '{"status": "FINISHED"}' | $HTTP_PUT_CMD
        break
    fi
    sleep 30
done

resultUrl_raw=$(curl --user $USER \
	$BASEURL/job/full_benchmark/$jenkinsJobId/api/json | jq '.url')
resultUrl=${resultUrl_raw//\"/}
Show $resultUrl

LOGBASEURL="$BASEURL/job"
logUrl=$LOGBASEURL/full_benchmark/$jenkinsJobId/consoleText
logJobId=$(curl $logUrl --user $USER -k | grep 'benchmark #' |awk -F ' ' '{print $4}')
logJobId_trim=${logJobId/\#/}
logResult=$LOGBASEURL/benchmark/$logJobId_trim/consoleText
logContent_raw="$(curl $logResult --user $USER -k | grep -E 'log_url.*' | awk -F 'log_url' '{print $2}' | awk -F ',' '{print $1}' | awk -F ' ' '{print $2}')"
logContent=${logContent_raw//\'/}
Show "Artifactory url: $logContent"

execution_url="$(curl $logResult --user $USER -k | grep -E 'log_url.*' | awk -F 'execution_json' '{print $2}' | awk -F ',' '{print $1}' | awk -F ' ' '{print $2}' )"
execution_url_1=${execution_url//\}/}
execution_url_trim=${execution_url_1//\'/}
echo $execution_url_trim

echo {\"result_link\": \"$execution_url_trim\"} | $HTTP_PUT_CMD

sendEmail "<html><body><p>Jenkins url: <br/>$resultUrl<br/>Artifactory url: <br/>$logContent<br/></p></body></html>"
clearLocalMediaFile
AfterShell
