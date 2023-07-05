#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
# this file include some common functions in validation pipeline
import paramiko
import subprocess # nosec
import logging
import os
import hashlib
import yaml
import operator

if (os.getenv('debug', '') == "true"):
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def sha256(content=None):
    if content is None:
        return ''
    sha256gen = hashlib.sha256()
    sha256gen.update(content.encode())
    sha256code = sha256gen.hexdigest()
    sha256gen = None
    return sha256code

def execute_cmd(cmd):
    """
    execute shell command
    :param cmd:
    :return: return exit code and output
    """
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    status = 1 if err else 0
    return status, output

def get_platforms(run_folder):
    """
    get platform list from benchmark run
    :param run_folder:
    :return:
    """
    platform_list = []
    for run in os.listdir(run_folder):
        if run != 'execution.json':
            platform = run.split("_")[0]
            platform_list.append(platform)
    return list(set(platform_list))

def workload_params_to_yaml(workload_params):
    """
    Convert the workload params str to yaml file for ctest, e.g: TEST_CONFIG=<test_config_path>/test_config.yaml ctest -R ...
    :param workload_params: workload_params opens in validation pipeline, forat as: param1:value1;param2:value2
    :return: generate test_config.yaml file in workspace
    """
    test_config_file = os.path.join(os.environ['WORKSPACE'], "test_config.yaml")
    if workload_params == '':
        os.system("touch %s" %test_config_file)
        pass
    else:
        test_config = {}
        test_config['*'] = {}
        for param in workload_params.split(" "):
            param_name = param.split("=")[0]
            param_value = param.split("=")[1]
            test_config['*'][param_name] = param_value
        with open(test_config_file, 'w+', encoding='utf-8') as file:
            file.write(yaml.safe_dump(test_config))

def get_available_cluster(cluster_config, cluster_info, platform, run_on_hw='', gated=False):
    required_worker_number = 0
    client_number = 0
    worker_number = 0
    # get required cluster info
    with open(cluster_config, "rt") as fd:
        required_cluster = yaml.safe_load(fd)
    required_cluster_details = {}
    cl_need_label = False
    for cl in required_cluster['cluster']:
        if 'labels' in cl.keys():
            required_worker_number = required_worker_number + 1
            label_list = []
            for label, value in cl['labels'].items():
                if gated is False:
                    if value == 'required' or value == 'preferred':
                        label_list.append(label)
                        cl_need_label = True
                else:
                    if value == 'required':
                        label_list.append(label)
                        cl_need_label = True
            if 'vm_group' in cl.keys():
                if cl['vm_group'] == 'client':
                    node_name = 'node_%s_%s-%s' %(required_worker_number, cl['vm_group'], client_number)
                    client_number = client_number + 1
                else:
                    node_name = 'node_%s_%s-%s' %(required_worker_number, cl['vm_group'], worker_number)
                    worker_number = worker_number + 1
            else:
                node_name = 'node_%s_worker-%s' %(required_worker_number, worker_number)
                worker_number = worker_number + 1
            #if cl_need_label is True:
            required_cluster_details[node_name] = label_list
    with open(cluster_info, "rt") as fd:
        clusters = yaml.safe_load(fd)

    available_cluster = []
    available_cluster_details = {}
    reserved_info = {}
    for cluster in clusters[platform]:
        info = sorted(cluster.values())[0]
        if len(info['workers']) < required_worker_number:
            continue
        if len(required_cluster_details.keys()) == 0:
            available_cluster.append(cluster.keys())
            available_cluster_details[''.join(cluster.keys())] = {}
            continue
        available_nodes = {}
        for node, label_list in required_cluster_details.items():
            node_reserved = False
            available_node_list = []
            for server in info['workers']:
                name = sorted(server.keys())[0]
                worker = sorted(server.values())[0]
                if run_on_hw == '': #check server with label
                    i = 0
                    for label in label_list:
                        if label in worker['labels']:
                            i = i + 1
                    if i == len(label_list):
                        available_node_list.append(name)
                    if name in reserved_info:
                        continue
                    else:
                        if i == len(label_list):
                            for reserve_ip, reserve_node in reserved_info.items():
                                if reserve_node == node:
                                    node_reserved = True
                            if node_reserved is False:
                                reserved_info[name] = node
                else:
                    if str(worker['hw_config']) == str(run_on_hw):
                        available_node_list.append(name)
                    if name in reserved_info:
                        continue
                    else:
                        if str(worker['hw_config']) == str(run_on_hw):
                            for reserve_ip, reserve_node in reserved_info.items():
                                if reserve_node == node:
                                    node_reserved = True
                            if node_reserved is False:
                                reserved_info[name] = node
            if len(label_list) == 0: #for null label node
                available_nodes["null_%s" %node] = available_node_list
            else:
                available_nodes[node] = available_node_list
        if len(reserved_info) == len(required_cluster_details.keys()):
            available_cluster.append(''.join(cluster.keys()))
            available_nodes = dict(sorted(available_nodes.items(),key=operator.itemgetter(0)))
            available_cluster_details[''.join(cluster.keys())] =  available_nodes

    return available_cluster_details, cl_need_label

def get_single_cluster(cluster_name, cluster_info):
    for cluster in cluster_info:
        if cluster_name in cluster:
            return cluster[cluster_name]

def get_single_worker(worker_name, worker_info):
    for worker in worker_info:
        if worker_name in worker:
            return worker[worker_name]
