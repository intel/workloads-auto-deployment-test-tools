#!/usr/bin/env bash

# progress

curl -u minghui@Password123! -X PUT "http://10.67.121.100:8899/local/api/job/15/" -H  "accept: application/json" -H  "Content-Type: application/json" -H  "X-CSRFToken: 86huWikA9Sw6QtUQv9mphTS4xT9NhkfhYDqqb9JBj91js7uFNNPrQzevvmQM2RYt" -d "{   \"progress\": 100}"

# status
# [ NOT_START, RUNNING, FAILED, FINISHED ]

# curl -X PUT "http://10.67.121.100:8899/local/api/job/15/" -H  "accept: application/json" -H  "Content-Type: application/json" -H  "X-CSRFToken: 86huWikA9Sw6QtUQv9mphTS4xT9NhkfhYDqqb9JBj91js7uFNNPrQzevvmQM2RYt" -d "{  \"status\": \"FINISHED\"}"
