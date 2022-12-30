dockerDaemon="/etc/docker/daemon.json"
registry=$1
need_restart=false
if [ -f $dockerDaemon ]
then
    out=$(cat $dockerDaemon | grep "$registry")
    echo $out
    if [ "$out" == "" ]
    then
        echo "Add registry: '$registry' to '$dockerDaemon'"
        need_restart=true
        jq --arg new "$registry" '."insecure-registries"? += [$new]' $dockerDaemon > /tmp/temp_daemon
        cat /tmp/temp_daemon > $dockerDaemon
    else
        echo "Insecure registry already configured"
    fi
else
    echo "No '$dockerDaemon' found, add a new one"
    need_restart=true
    echo "{\"insecure-registries\": [\"$registry\"]}" > $dockerDaemon
fi
if [ "$need_restart" == "true" ]
then
    echo "Restarting docker..."
    systemctl daemon-reload
    systemctl restart docker
fi

