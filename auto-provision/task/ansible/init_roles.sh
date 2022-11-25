#!/usr/bin/env bash

configFilesPath="../conf/"
baseFunctions="../scripts/base.sh"
configFileShPath=$configFilesPath$1.sh
configFileYamlPath=$configFilesPath$1.yaml
configFileIniPath=$configFilesPath$1.ini
roles=$(ls ./roles)

cat $configFileIniPath > "inventory/inventory.ini"
for role in ${roles[@]}
do
	cat $configFileYamlPath > "./roles/${role}/vars/main.yml"
	cat $configFileShPath > "./roles/${role}/files/workload.sh"
	cat $baseFunctions > "./roles/${role}/files/base_function.sh"
done



