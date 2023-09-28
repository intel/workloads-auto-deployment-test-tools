#!/bin/bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
set -o pipefail
# set -v  if want to show more log
if [ -z "$1" ]; then
  echo "Usage: [options] <user>@<ip> [<user>@<ip> ...] [--port=<port>] [--restart]"
  echo "<user>@<ip>: test@1.1.1.1 for example"
  echo "--port=<port>: --port=22 for example"
  echo "--restart: No user input, just try to restart all components, use this option if already successfully installed"
  echo "--add_instance: copy and update setup/cert/<IP>:5000.crt to newly added machines"
  exit 3
fi
restart=false
add_instance=false
ssh_port=22
all_hosts=()
debug_flag=""
i=0
for v in $@; do
  if [[ "$v" =~ "@" ]]; then
    all_hosts[$i]=$v
    i=$((i+1))
  fi
  
  case "$v" in
  --port=*)
    ssh_port="${v#--port=}"
    ;;
  --restart*)
    restart=true
    ;;
  --add_instance*)
    add_instance=true
    ;;
  --debug*)
    debug_flag="-v"
    ;;
  esac
done
host0=${all_hosts[0]}
twdt_host="$(
    cat <<EOF
        twdt:
          ansible_user: "${host0/@*/}"
          ansible_host: "${host0/*@/}"
          ansible_port: "$ssh_port"
EOF
)"
echo $twdt_host
DIR="$(dirname "$(readlink -f "$0")")"
$DIR/script/setup-ansible.sh
$DIR/script/setup-native.sh ${all_hosts[@]} 
[ -d $DIR/ansible_log ] || mkdir $DIR/ansible_log
log_suffix=$(date +%F_%H-%M-%S)
if [ $restart == 'false' ] && [ $add_instance == 'false' ]; then
  ANSIBLE_ROLES_PATH=./roles ANSIBLE_INVENTORY_ENABLED=yaml ansible-playbook ${debug_flag} --inventory <(cat <<EOF
all:
  children:
    twdt_host:
      hosts:
$twdt_host
EOF
) -e http_proxy=$http_proxy -e https_proxy=$https_proxy -e no_proxy=$no_proxy $DIR/script/twdt-prepare.yaml | tee $DIR/ansible_log/twdt_ansible_setup_${log_suffix}.log
  if [ $? -ne 0 ]; then
    echo "twdt prepare stage failed."
    exit 3
  fi
fi
get_user_input(){
  read -s -p "Now, please tell me current user's(${host0/@*/}) password [used to add current host to be Jenkins agent]:" TWDTOSPassword
  while ! python3 -c "
import paramiko,sys;
host = '${host0/*@/}';
username = '${host0/@*/}';
password = '$TWDTOSPassword';
port = ${ssh_port};
client = paramiko.client.SSHClient();
client.set_missing_host_key_policy(paramiko.AutoAddPolicy());
try:
    client.connect(host, username=username, password=password, port=port, look_for_keys=False);
    client.exec_command('ls');
except Exception as ex:
    print('\n' + str(ex))
    sys.exit(1)
    "
  do
  read -s -p $'\nPassword verfy failed please try again: ' TWDTOSPassword
  done
  echo Ok, please confirm whether you input right information you want to be used for each component:
  echo Then, please input some necessary information for installation script to set for TWDT system:
  TWDTJenkinWorkspaceDir=$DIR/../jenkins/runtime/
  mkdir -p $TWDTJenkinWorkspaceDir
  read -p "[1/5] Enter the password that you want to use to login the TWDT web portal. [CANNOT be empty]:" TWDTPortalPassword
  read -p "[2/5] Enter password you want to be used to login Jfrog artifactory repository. [must be a STRONG password, ]:" TWDTJfrogPassword
  while ! echo "$TWDTJfrogPassword" | grep -Pq '(?=^.{8,255}$)(?=^[^\s]*$)(?=.*\d)(?=.*[A-Z])(?=.*[a-z])'
  do
    read -p $'\nPlease enter a strong password: ' TWDTJfrogPassword
  done
  read -p "[3/5] Enter password you want to be used to login Jenkins service. [CANNOT be empty]:" TWDTJenkinsPassword
  read -p "[4/5] Enter password you want to be used for Postgres database connection. [CANNOT be empty]:" TWDTPostgresPassword
  read -p "[5/5] Enter password you use when sending EMails from your SMTP server. [if not necessary, please leave it blank]:" TWDTEmailSenderPassword

  env_for_prepare+=" -e TWDTOSPassword=$TWDTOSPassword"
  env_for_prepare+=" -e TWDTJenkinsPassword=$TWDTJenkinsPassword"
  env_for_prepare+=" -e TWDTJenkinWorkspaceDir=$TWDTJenkinWorkspaceDir"
  env_for_prepare+=" -e TWDTJfrogPassword=$TWDTJfrogPassword"
  env_for_prepare+=" -e TWDTPortalPassword=$TWDTPortalPassword"
  env_for_prepare+=" -e TWDTPostgresPassword=$TWDTPostgresPassword"
  env_for_prepare+=" -e TWDTEmailSenderPassword=$TWDTEmailSenderPassword"
  env_for_prepare+=" -e http_proxy=$http_proxy"
  env_for_prepare+=" -e https_proxy=$https_proxy"
  env_for_prepare+=" -e no_proxy=$no_proxy"
  echo ""
  echo "[1/5] TWDT portal password: $TWDTPortalPassword"
  echo "[2/5] Jenkins password: $TWDTJenkinsPassword"
  echo "[3/5] Jfrog password: $TWDTJfrogPassword"
  echo "[4/5] Postgres database's connection password: $TWDTPostgresPassword"
  echo "[5/5] SMTP server's password: $TWDTEmailSenderPassword"
  read -n 1 -s -r -p "If that's all right, please hit ENTER to continue, otherwise press CTRL + C to exit."
}
if [ $restart == 'false' ] && [ $add_instance == 'false' ]; then
  get_user_input
  env_for_prepare+=" -e TWDTHost=${host0/*@/} -e TWDTHostUser=${host0/@*/} -e TWDTHostPort=$ssh_port"
  ANSIBLE_ROLES_PATH=./roles ANSIBLE_INVENTORY_ENABLED=yaml ansible-playbook ${debug_flag} --inventory <(cat <<EOF
all:
  children:
    twdt_host:
      hosts:
$twdt_host
EOF
) $env_for_prepare $DIR/script/twdt-presetup.yaml | tee -a $DIR/ansible_log/twdt_ansible_setup_${log_suffix}.log
  if [ $? -ne 0 ]; then
    echo "twdt presetup stage failed."
    exit 3
  fi
fi
. /etc/profile
if [ "${VAULT_KEY1}" == "" ];then

    echo "Seems like no VAULT_KEY[1,2,3] key in /etc/profile, if lost please reinstall vault and install it with setup-twdt.sh as install-guide.md showed"
    exit 3
fi
timeout 1 vault operator unseal "$VAULT_KEY1" && timeout 1 vault operator unseal $VAULT_KEY2 && timeout 1 vault operator unseal $VAULT_KEY3
env_for_setup=$(vault kv get -format=json kv/wsf-secret-password | python3 -c 'import os,sys,json; data=json.load(sys.stdin)["data"];print("-e"," -e ".join([(f"{k}={data[k]}") for k in data]))')

$DIR/script/setup-reg.sh ${host0/*@/} ${all_hosts[@]:1} --add_instance=${add_instance}
if [ $? -ne 0 ]; then
  echo "twdt setup registry step failed."
  exit 3
fi
if [ $restart == 'false' ] && [ $add_instance == 'true' ]; then
   echo "Update all hosts cerfications finished"
   exit 0
fi
all_ansible_hosts="$(
  for h in ${all_hosts[@]}; do
      cat <<EOF
        twdt-${h/*@/}:
          ansible_user: "${h/@*/}"
          ansible_host: "${h/*@/}"
          ansible_port: "${ssh_port}"
EOF
done)"
echo $all_ansible_hosts
if [[ $https_proxy ]]; then
  ProxyHost=`echo $https_proxy | awk -F[/:] '{print $4}'`
  ProxyPort=`echo $https_proxy | awk -F[/:] '{print $5}'`
fi
env_for_setup+=" -e ProxyHost=$ProxyHost"
env_for_setup+=" -e ProxyPort=$ProxyPort"
ANSIBLE_ROLES_PATH=./roles ANSIBLE_INVENTORY_ENABLED=yaml ansible-playbook ${debug_flag} --inventory <(cat <<EOF
all:
  children:
    twdt_host:
      hosts:
$twdt_host
    all_hosts:
      hosts:
$all_ansible_hosts
EOF
)  ${env_for_setup} $DIR/script/twdt-setup.yaml | tee -a $DIR/ansible_log/twdt_ansible_setup_${log_suffix}.log
if [ $? -eq 0 ]; then
  echo "Congratulation! Seems like everything going well, Please check doc/install-guide.md to make sure setup successfully."
else
  echo "Some step failed, Please check the output log."
fi
