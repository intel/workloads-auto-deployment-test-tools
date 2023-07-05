#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
source /etc/profile
TEST_PATH="/tmp"
LOG_FILE="$TEST_PATH/crontab.log"
touch $LOG_FILE
FRONTAPI=$1
QUEUEAPI="$FRONTAPI/local/api/queue/"
portalUserName=$(vault kv get kv/wsf-secret-password | grep portalUserName | awk -F ' ' '{print($2)}')
portalPassword=$(vault kv get kv/wsf-secret-password | grep portalPassword | awk -F ' ' '{print($2)}')
CURRENT_TIME=$(TZ=UTC-8 date +%Y-%m-%d" "%H:%M:%S)
TAG="[$CURRENT_TIME]"
HTTPRES=$(http get $QUEUEAPI --auth $portalUserName:$portalPassword --verify=no)
echo $TAG >> $LOG_FILE
echo $HTTPRES >> $LOG_FILE
