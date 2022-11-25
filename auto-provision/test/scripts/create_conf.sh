#!/usr/bin/env bash
set -x
#curl -H "Content-Type: application/json" -X POST -d @demo.json localhost:8089/conf/createconf
#curl -H "Content-Type: application/json" -X POST -d @data-2022-05-24.json localhost:8089/conf/createconf
curl -H "Content-Type: application/json" -X POST -d @test1.json localhost:8089/conf/createconf

