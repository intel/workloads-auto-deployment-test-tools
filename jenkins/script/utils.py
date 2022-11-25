# this file include some common functions in validation pipeline
#import paramiko
import subprocess
import logging
from lxml import html
import requests, datetime
import os
import hashlib
import yaml

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

def execute_remote_cmd(ip, user, key, cmd, port):
    """
    execute command on remote host using local key
    :param ip:
    :param key:
    :param cmd:
    :param port:
    :return:
    """
    try:
        ssh = paramiko.SSHClient()
        # add to host_allow
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(key)
        ssh.connect(hostname=ip,
                    port=port,
                    username=user,
                    pkey=pkey)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        ssh.close()
        return output
    except:
        print("Exception exists")

def clean_collectd_and_namespace(controller_ip, controller_user, controller_port, worker_ip, worker_user,
                                 worker_port):
    """
    make sure all collectd processes and previous canceled namespace are cleaned before running cumulus
    :param controller_ip: k8s master ip
    :param controller_user: k8s master ssh user
    :param controller_port: k8s master ssh port
    :param worker_ip: k8s worker ip
    :param worker_user: k8s worker ssh user
    :param worker_port: k8s worker ssh port
    :return:
    """
    key = '/root/.ssh/id_rsa'
    cmd = 'ps -ef |grep collectd |grep -v grep |wc -l'
    collectd_count = execute_remote_cmd(worker_ip, worker_user, key, cmd, worker_port)
    if collectd_count:
        if int(collectd_count) > 0:
            cmd = "ps -ef |grep collectd |grep -v grep|awk '{print $2}'"
            collectd_ids = execute_remote_cmd(worker_ip, worker_user, key, cmd, worker_port)
            for id in collectd_ids.split('\n'):
                if id != '':
                    kill_cmd = 'sudo kill -9 %s & wait $!' % id
                    execute_remote_cmd(worker_ip, worker_user, key, kill_cmd, worker_port)

    namespace_list = execute_remote_cmd(controller_ip, controller_user, key, "kubectl get ns | awk '{print $1}'",
                                        controller_port)
    for ns in namespace_list.split('\n'):
        if ns != 'NAME':
            count = ns.split("-")
            if len(count) == 5 or len(count) == 6:
                logging.info(ns)
                cmd = "kubectl get pods -n %s -o wide|grep `kubectl  get nodes -o wide | grep %s | awk '{print $1}'`|wc -l" % (
                ns, worker_ip)
                old_pod_number = execute_remote_cmd(controller_ip, controller_user, key, cmd, controller_port)
                old_pod_number = old_pod_number.split('\n')[0]
                if int(old_pod_number) > 0:
                    cmd = "kubectl delete ns %s & wait $!" % ns
                    execute_remote_cmd(controller_ip, controller_user, key, cmd, controller_port)

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
    if workload_params == '':
        pass
    else:
        test_config = {}
        test_config['*'] = {}
        for param in workload_params.split(";"):
            param_name = param.split(":")[0]
            param_value = param.split(":")[1]
            test_config['*'][param_name] = param_value
        test_config_file = os.path.join(os.getenv("WORKSPACE",""), "test_config.yaml")
        with open(test_config_file, 'w+', encoding='utf-8') as file:
            file.write(yaml.safe_dump(test_config))
