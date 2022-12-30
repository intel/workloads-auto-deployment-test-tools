#!/usr/bin/python3
import time
import os
import logging
import subprocess # nosec
import yaml
import sys
import json
import random
from utils import clean_collectd_and_namespace, get_available_cluster, get_single_cluster, get_single_worker
import re

if (os.getenv('debug', '') == "true"):
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Benchmark(object):
    def __init__(self, benchmark_config, cluster_config, run_uri, tmp_dir, benchmark_option, gated):
        self.CLUSTER_FILE = os.path.join(os.environ['WORKSPACE'], "pool", "cluster.yaml")
        self.HW_HISTORY = os.path.join(os.environ['WORKSPACE'], "pool", "execution_hw.json")
        self.WORKLOAD = os.environ['workload']
        self.platform = os.environ['platform']
        self.CUMULUS_CONFIG = os.path.join(os.environ['WORKSPACE'], "validation/script/cumulus/cumulus-config.yaml")
        self.benchmark_config = benchmark_config
        self.CLUSTER_CONFIG = cluster_config
        self.run_uri = run_uri
        self.tmp_dir = tmp_dir
        self.backend = os.getenv("backend", 'cumulus')
        self.gated = gated
        self.benchmark_option = benchmark_option
        self.NO_LABEL_FOUND_FILE = os.path.join(os.path.dirname(self.benchmark_config), "no_label_found")
        self.NO_ENOUGH_WORKERS_CLUSTER_FILE = os.path.join(os.path.dirname(self.benchmark_config), "no_enough_workers_cluster")
        self.SKIP_SPECIFIED_NUM_NODES_CASE_FILE = os.path.join(os.path.dirname(self.benchmark_config),"skip_specified_num_nodes_case")
        self.TIMEOUT_WAIT_FOR_SERVER_FILE = os.path.join(os.path.dirname(self.benchmark_config), "timout_wait_for_server")
        self.CTESTSH_OPTIONS = os.getenv('CTESTSH_OPTIONS', '')
        self.st_options = os.getenv('st_options', '')
        self.options = os.getenv('options', '')
        self.CLUSTER_HW_CONFIG = os.path.join(os.path.dirname(self.benchmark_config), "cluster_config")
        self.LOGDIR = os.path.dirname(self.benchmark_config)

    def run_benchmark(self, cmd):
        # run pkb.py for cumulus or start.sh for terraform
        logging.info(cmd)
        p = subprocess.Popen(
            cmd,
            shell=True,
            cwd=os.path.dirname(self.benchmark_config),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        try:
            while True:
                line = p.stdout.readline()
                logging.info('[stdout] : %s', line)
                if not line:
                    break
        except Exception as e:
            logging.info(e)
        while p.poll() is None:
            time.sleep(0.5)
        return p.returncode

    def update_terraform_config(self, cluster_controller, cluster_workers, sut_type, registry, prometheus_url, gated=False):
        terraform_config = {}

        variable_controller = 'controller_profile'
        variable_worker = 'worker_profile'
        variable_client = 'client_profile'
        terraform_config[variable_controller] = {}

        terraform_overwrite_config_file = os.path.join(self.LOGDIR, 'variable-values.json')

        controller = {}
        controller['user_name'] = cluster_controller['user']
        controller['public_ip'] = cluster_controller['ip']
        controller['private_ip'] = cluster_controller['internal_ip']
        terraform_config[variable_controller]['vm_count'] = 1
        terraform_config[variable_controller]['hosts'] = {}
        terraform_config[variable_controller]['hosts']['controller-0']=controller

        worker_vm_count = 0
        client_vm_count = 0

        for node, server in cluster_workers.items():
            worker_name = node.split('_')[-1]
            worker = {}
            worker['public_ip'] = server['ip']
            worker['user_name'] = server['user']
            if 'internal_ip' in server:
                worker['private_ip'] = server['internal_ip']
            else:
                worker['private_ip'] = server['ip']

            if 'worker' in worker_name:
                if variable_worker not in terraform_config:
                    terraform_config[variable_worker] = {}
                    terraform_config[variable_worker]['hosts'] = {}
                terraform_config[variable_worker]['hosts'][worker_name] = worker
                worker_vm_count = worker_vm_count + 1
            else:
                if variable_client not in terraform_config:
                    terraform_config[variable_client] = {}
                    terraform_config[variable_client]['hosts'] = {}
                terraform_config[variable_client]['hosts'][worker_name] = worker
                client_vm_count = client_vm_count + 1

        if worker_vm_count > 0:
            terraform_config[variable_worker]['vm_count'] = worker_vm_count
        if client_vm_count > 0:
            terraform_config[variable_client]['vm_count'] = client_vm_count

        variable_sut_machine_type = "intel_publisher_sut_machine_type"
        variable_sut_metadata = "intel_publisher_sut_metadata"

        terraform_config[variable_sut_machine_type] = sut_type
        terraform_config[variable_sut_metadata] = "CPU:%s,Memory:%s,PCH:%s,IFWI:%s,OS:%s,Kernel:%s,Kubernetes:%s,Docker:%s,Microcode:%s,PCIE:%s,NIC:%s,BOOT:%s" % (
                    server['hw_info']['CPU'], server['hw_info']['Memory'], server['hw_info']['PCH'],
                    server['hw_info']['IFWI'], server['hw_info']['OS'], server['hw_info']['Kernel'],
                    server['hw_info']['Kubernetes'], server['hw_info']['Docker'],
                    server['hw_info']['Microcode'], server['hw_info']['PCIE'], server['hw_info']['NIC'], server['hw_info']['BOOT'])

        with open(terraform_overwrite_config_file, 'w+', encoding='utf-8') as file:
            cumulus_config_info = json.dumps(terraform_config, indent=4)
            logging.info("=========================================================")
            logging.info(terraform_overwrite_config_file)
            logging.info(cumulus_config_info)
            logging.info("=========================================================")
            file.write(cumulus_config_info)

        # run terraform start.sh
        cmd = 'bash -c \'set -o pipefail;/opt/script/start.sh %s '"%s"' %s 2>&1 | tee "%s/tfplan.logs" \' ' %(self.benchmark_option, self.st_options, self.CTESTSH_OPTIONS, self.LOGDIR)
        logging.info(cmd)
        tf_return_code = self.run_benchmark(cmd)
        return tf_return_code

    def run(self):
        # for cumulus container clean up
        with open(os.path.join(os.getenv("WORKSPACE", ""), "run_uri"), "a+") as fd:
            fd.write(self.run_uri)
        # get required cluster info
        with open(self.CLUSTER_CONFIG, "rt") as fd:
            required_cluster = yaml.safe_load(fd)
        logging.info("Cluster config:")
        logging.info(required_cluster)

        build_id = os.getenv('build_id', '0000')
        required_worker_number = 0

        required_label = []
        required_ai_label = False
        for cl in required_cluster['cluster']:
            if 'labels' in cl.keys():
                required_worker_number = required_worker_number + 1
                for label, value in cl['labels'].items():
                    if label == 'HAS-SETUP-BKC-AI':
                        required_ai_label = True
                    if value == 'required' or value == 'preferred':
                        required_label.append(label)
        if os.getenv('specified_node_number', '') != '':
            required_worker_number = int(os.environ['specified_node_number'])
            logging.info('use specified node number %s' %required_worker_number)
        else:
            logging.info('no specified node number')
        cloud_validation = False
        return_code = 0

        # get cluster type
        log_folder = self.benchmark_config.split("/")[-2]
        cluster_type = log_folder.split("logs-")[1].split("-")[0].split("_")[0]

        if cluster_type == 'baremetal' or cluster_type == 'snc4' or cluster_type == 'static':
            platform = self.platform
        elif cluster_type == 'vm':
            platform = self.platform + '-VM'
        elif cluster_type == 'tdx':
            platform = self.platform + '-TDX'
        elif cluster_type == 'cit':
            platform = self.platform + '-GATED'
        else:
            platform = cluster_type.upper()
            cloud_validation = True
            logging.info("no need to update cumulus config for cloud validation.")

        test_case_name = cluster_type + log_folder.split(cluster_type)[1]
        sut_type = self.platform

        # check is larger than the specified number of case nodes or not
        limited_node_number = int(os.getenv("limited_node_number", "1"))
        # k8s_worker_list = os.getenv("worker_ip_list", "")
        # worker_number = len(k8s_worker_list.split(","))
        if required_worker_number > limited_node_number:
            logging.info("This case needs %s nodes and larger than the user specified limit num: %s, skip it ..." %
                         (required_worker_number, limited_node_number))
            os.mknod(self.SKIP_SPECIFIED_NUM_NODES_CASE_FILE)
            sys.exit(3)

        # get all static cluster info
        with open(self.CLUSTER_FILE, "rt") as fd:
            clusters = yaml.safe_load(fd)
        #required_label = []
        registry = ''
        prometheus_url = ''
        required_worker_available = False
        required_worker_exists = False
        worker_label_not_found_cluster_count = 0
        worker_ip_not_reachable_cluster_count = 0
        worker_other_mismatch_cluster_count = 0
        timeout_count_max = 2 #total 4 mins
        timeout_count = 0

        available_cluster, cl_label_needed = get_available_cluster(self.CLUSTER_CONFIG, self.CLUSTER_FILE, platform,'', False)
        logging.info("Available cluster info:")
        logging.info(available_cluster)
        if len(available_cluster.keys()) == 0:
            if cl_label_needed is True:
                logging.info("no matched label server found, exit........")
            else:
                logging.info(
                    "no cluster has enough nodes, test needs %s nodes, exit........" % required_worker_number)
            os.system("touch %s" % self.NO_LABEL_FOUND_FILE)
            sys.exit(3)

        while True:
            if timeout_count < timeout_count_max:
                logging.info("available clusters are %s" %available_cluster.keys())
                for cluster, cluster_info in available_cluster.items():
                    if required_worker_available is True:
                        break
                    i = 0
                    cluster_controller = {}
                    cluster_workers = {}
                    logging.info('check servers in cluster %s' % cluster)
                    current_cluster = get_single_cluster(cluster, clusters[platform])
                    # check controller, if it is not reachable, skip to another cluster
                    controller_ip = current_cluster['master']['ip']
                    controller_user = current_cluster['master']['user']
                    controller_port = current_cluster['master']['port']
                    if 'internal_ip' in current_cluster['master']:
                        controller_internal_ip = current_cluster['master']['internal_ip']
                    else:
                        controller_internal_ip = controller_ip
                    logging.info(f"Check is crontoler: {controller_ip} reachable")
                    logging.info("ssh -p %s %s@%s 'ls /tmp' > /dev/null" %
                                            (controller_port, controller_user, controller_ip))
                    if os.system("ssh -p %s %s@%s 'ls /tmp' > /dev/null" %
                                            (controller_port, controller_user, controller_ip)) == 0:
                        logging.info(f"Crontoler: {controller_ip} is reachable")
                        cluster_controller['ip'] = controller_ip
                        cluster_controller['user'] = controller_user
                        cluster_controller['port'] = controller_port
                        cluster_controller['internal_ip'] = controller_internal_ip
                    else:
                        logging.info("controller %s is not reachable in cluster %s, will try again......" % (controller_ip, cluster))
                        continue
                    #Use this variable to avoid chossing duplicated worker
                    choosed_server_list = []
                    for node, workers in cluster_info.items():
                        logging.info("start to check available server for %s" % node)
                        for worker in workers:
                            current_worker = get_single_worker(worker, current_cluster['workers'])
                            ip = current_worker['ip']
                            ssh_port = current_worker['port']
                            ssh_user = current_worker['user']
                            if ip not in choosed_server_list:
                                # check server is reachable or not
                                logging.info(f"Check is worker: {ip} reachable")
                                logging.info("ssh -p %s %s@%s 'ls /tmp' > /dev/null"
                                                        % (ssh_port, ssh_user, ip))
                                if os.system("ssh -p %s %s@%s 'ls /tmp' > /dev/null"
                                                        % (ssh_port, ssh_user, ip)) == 0:
                                    logging.info(f"Worker: {ip} is reachable")
                                    node_name = 'node' + node.split('node')[-1]
                                    cluster_workers[node_name] = current_worker
                                    i = i + 1
                                    hw_config = current_worker['hw_config']
                                    choosed_server_list.append(ip)
                                    break
                                else:
                                    # need enhance if server is down all the time...
                                    logging.info("%s is unreachable. :" % ip)
                            else:
                                logging.info(f"Worker '{ip}' is already choosed")
                    if i >= required_worker_number:
                        os.system(
                            "echo %s > %s" % (hw_config, self.CLUSTER_HW_CONFIG))
                        registry = current_cluster['docker_registry']
                        if 'powerstat_prometheus_url' in current_cluster:
                            prometheus_url = current_cluster['powerstat_prometheus_url']
                        required_worker_available = True
                    else:
                        logging.info(f"Required worker number is: {required_worker_number}, available node number is: {i}")

                if required_worker_available is True:
                    logging.info("already found matched server, continue testing......")
                    break
                timeout_count = timeout_count + 1
                sleep_sec = 120
                logging.info(f"Wait for {sleep_sec} to check cluster conectivity again")
                time.sleep(sleep_sec)
            else:
                logging.info("timeout wait for available work ready, exit......")
                os.system("touch %s" % self.TIMEOUT_WAIT_FOR_SERVER_FILE)
                sys.exit(3)
                break
        if required_worker_available is True:
            # update terraform config
            logging.info("Update terraform config")
            logging.info(cluster_controller)
            logging.info(cluster_workers)
            logging.info(sut_type)
            logging.info(registry)
            logging.info(prometheus_url)
            return_code = self.update_terraform_config(cluster_controller, cluster_workers, sut_type, registry, prometheus_url, False)
            sys.exit(return_code)

if __name__ == '__main__':
    test_cluster_config = sys.argv[1]
    benchmark_config = sys.argv[2]
    run_uri = sys.argv[3]
    tmp_dir = sys.argv[4]
    benchmark_option = sys.argv[5]
    gated = sys.argv[6]

    Benchmark = Benchmark(benchmark_config, test_cluster_config, run_uri, tmp_dir, benchmark_option, gated)
    Benchmark.run()
