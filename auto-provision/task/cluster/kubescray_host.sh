#!/usr/bin/env bash
configFileName="$1"
source "../scripts/base.sh"
source "../conf/$configFileName.sh"

declare -a IPS=()
function getIP() {
    for ((i = 1; i < ${#deployHost[@]}; i++)); do
        ip=$(echo ${deployHost[$i]} | awk -F"," '{print $3}')
        echo "$ip"
        IPS[$i]="$ip"
   done
}


function configCluster() {
    allYamlPath="./inventory/mycluster/group_vars/all/all.yml"
    k8sClusterYamlPath="./inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml"
    addonsYamlPath="./inventory/mycluster/group_vars/k8s_cluster/addons.yml"
    cp -f "../all.yml" "$allYamlPath"
    cp -f "../k8s-cluster.yml" "$k8sClusterYamlPath"
    cp -f "../addons.yml" "$addonsYamlPath"
    sed -i "s/{{kube_version}}/${kubernetesArgs["kube_version"]}/g" "$k8sClusterYamlPath"
    sed -i "s/{{kube_network_plugin}}/${kubernetesArgs["kube_network_plugin"]}/g" "$k8sClusterYamlPath"
    sed -i "s/{{container_manager}}/${kubernetesArgs["container_manager"]}/g" "$k8sClusterYamlPath"
    sed -i "s/{{dashboard_enabled}}/${kubernetesArgs["dashboard_enabled"]}/g" "$addonsYamlPath"
    sed -i "s/{{helm_enabled}}/${kubernetesArgs["helm_enabled"]}/g" "$addonsYamlPath"
    sed -i "s/{{registry_enabled}}/${kubernetesArgs["registry_enabled"]}/g" "$addonsYamlPath"
    sed -i "s/{{ingress_nginx_enabled}}/${kubernetesArgs["ingress_nginx_enabled"]}/g" "$addonsYamlPath"
    sed -i "s/{{ingress_nginx_host_network}}/${kubernetesArgs["ingress_nginx_host_network"]}/g" "$addonsYamlPath"
    sed -i "s/{{krew_enabled}}/${kubernetesArgs["krew_enabled"]}/g" "$addonsYamlPath"
}
function run() {
    cd "./kubespray"
    rm -rf inventory/mycluster
    cp -rfp inventory/sample inventory/mycluster
    configCluster
    #declare -a IPS=(10.10.1.3 10.10.1.4 10.10.1.5)
    CONFIG_FILE=inventory/mycluster/hosts.yaml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
    #cat inventory/mycluster/group_vars/all/all.yml
    #cat inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml
    #cat "./inventory/mycluster/group_vars/k8s_cluster/addons.yml"
    ansible-playbook -i inventory/mycluster/hosts.yaml --become --become-user=root cluster.yml
    cd -
}


printLine
if [ "$kubernetes_deploy" == "true" ]; then
    getIP
    echo "${IPS[@]}"
    run
fi
printLine
