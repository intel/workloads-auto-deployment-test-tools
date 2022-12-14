#!/usr/bin/env bash
jenkinsUserName=$(go run getSecret.go | grep "jenkinsUserName::" | awk -F':: ' '{print $2}')
jenkinsToken=$(go run getSecret.go | grep "jenkinsToken::" | awk -F':: ' '{print $2}')
jenkinsUrl=$(go run getSecret.go | grep "jenkinsUrl::" | awk -F':: ' '{print $2}')
statusUrl=$(go run getSecret.go | grep "statusUrl::" | awk -F':: ' '{print $2}')
echo "$jenkinsUserName"
echo "$jenkinsToken"
echo "$jenkinsUrl"
echo "$statusUrl"
