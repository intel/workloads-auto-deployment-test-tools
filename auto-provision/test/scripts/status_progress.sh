#!/usr/bin/env bash

# progress
curl -X PUT "http://10.67.121.100:8899/local/api/job/36/" -d "{  \"progress\": 100}"

# status
# [ NOT_START, RUNNING, FAILED, FINISHED ]

curl -X PUT "http://10.67.121.100:8899/local/api/job/100/" -H  -d "{  \"status\": \"FINISHED\"}"

