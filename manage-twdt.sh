#!/bin/bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
if [ -z "$1" ]; then
  echo "Usage: manage-twdt.sh [status|stop|start|restart]"
fi
DIR="$(dirname "$(readlink -f "$0")")"
start=false
stop=false
restart=false
status=false
last=""
for v in $@; do
  case "$v" in
    start|stop|restart|status)
    if [ "$v" = "status" ]; then
        status=true
        elif [ "$v" == "stop" ]; then
        stop=true
        elif [ "$v" = "start" ]; then
        start=true
        elif [ "$v" = "restart" ]; then
        restart=true
    fi
    ;;
    *)
    echo "Unsupported argument: $v"
    ;;
  esac
done

# status
get_status(){
  docker compose -f $DIR/portal/docker-compose.yml ps
  docker compose -f $DIR/jenkins/docker-compose.yml ps | grep -v "NAME        IMAGE"
}
# stop
stop_twdt(){
  docker compose -f $DIR/portal/docker-compose.yml stop
  docker compose -f $DIR/jenkins/docker-compose.yml stop
}
# start
start_twdt(){ 
  sudo systemctl start vault
  sleep 3
  . /etc/profile
  if [ "${VAULT_KEY1}" == "" ]; then

    echo "Seems like no VAULT_KEY[1,2,3] key in /etc/profile, if lost please reinstall vault and install it with setup-twdt.sh as install-guide.md showed"
    exit 3
  fi
  timeout 1 vault operator unseal $VAULT_KEY1 && timeout 1 vault operator unseal $VAULT_KEY2 && timeout 1 vault operator unseal $VAULT_KEY3
  docker compose -f $DIR/jenkins/docker-compose.yml up -d
  docker compose -f $DIR/portal/docker-compose.yml up -d
  #Ensure Jfrog started normally
  tries=0
  while ! docker exec jfrog bash -c "netstat -a|grep LISTEN|grep -q localhost:8046" 
  do
    tries=$((tries+1))
    if [ ${tries} -gt 5 ];then
      echo "Jfrog start failed, please try \"docker compose -f $DIR/jenkins/docker-compose.yml build jfrog\" and then \"docker compose -f $DIR/jenkins/docker-compose.yml start jfrog\" to start Jfrog."
      exit 3
    fi
    docker restart jfrog
    sleep 60
  done
}
# restart
restart_twdt(){ 
  sudo systemctl start vault
  sleep 3
  . /etc/profile
  if [ "${VAULT_KEY1}" == "" ]; then

    echo "Seems like no VAULT_KEY[1,2,3] key in /etc/profile, if lost please reinstall vault and install it with setup-twdt.sh as install-guide.md showed"
    exit 3
  fi
  timeout 1 vault operator unseal $VAULT_KEY1 && timeout 1 vault operator unseal $VAULT_KEY2 && timeout 1 vault operator unseal $VAULT_KEY3
  docker compose -f $DIR/portal/docker-compose.yml down
  docker compose -f $DIR/jenkins/docker-compose.yml down

  docker compose -f $DIR/jenkins/docker-compose.yml up -d
  docker compose -f $DIR/portal/docker-compose.yml up -d
  #Ensure Jfrog started normally
  tries=0
  while ! docker exec jfrog bash -c "netstat -a|grep LISTEN|grep -q localhost:8046" 
  do
    tries=$((tries+1))
    if [ ${tries} -gt 5 ];then
      echo "Jfrog start failed, please try \"docker compose -f $DIR/jenkins/docker-compose.yml build jfrog\" and then \"docker compose -f $DIR/jenkins/docker-compose.yml start jfrog\" to start Jfrog."
      exit 3
    fi
    docker restart jfrog
    sleep 60
  done
}

if [ "$status" == 'true' ]; then
    get_status
fi
if [ "$stop" == 'true' ]; then
    stop_twdt
fi
if [ "$start" == 'true' ]; then
    start_twdt
fi
if [ "$restart" == 'true' ]; then
    restart_twdt
fi