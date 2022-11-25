#!/usr/bin/python3
import time
import os
import logging
import subprocess
import yaml
import sys
import json
import random
# from utils import clean_collectd_and_namespace
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Provision(object):
    def __init__(self, cumuls_config, cluster_config, run_uri, tmp_dir, cumulus_option, gated):
        self.CLUSTER_FILE = os.path.join(os.getenv("WORKSPACE", ""), "pool", "cluster.yaml")
        self.HW_HISTORY = os.path.join(os.getenv("WORKSPACE", ""), "pool", "execution_hw.json")
        self.WORKLOAD = os.getenv("workload", "")
        self.platform = os.getenv("platform", "")
        self.CLUSTER_CONFIG = os.path.join(os.getenv("WORKSPACE", ""), "validation/workload", self.WORKLOAD,
                                           "cluster-config.yaml.m4")
        self.CUMULUS_CONFIG = os.path.join(os.getenv("WORKSPACE", ""), "validation/script/cumulus/cumulus-config.yaml")
        self.test_cumulus_config = cumuls_config
        self.CLUSTER_CONFIG = cluster_config
        self.run_uri = run_uri
        self.tmp_dir = tmp_dir
        self.gated = gated
        self.cumulus_option = cumulus_option
        self.NO_LABEL_FOUND_FILE = os.path.join(os.path.dirname(self.test_cumulus_config), "no_label_found")
        self.NO_ENOUGH_WORKERS_CLUSTER_FILE = os.path.join(os.path.dirname(self.test_cumulus_config),
                                                           "no_enough_workers_cluster")
        self.SKIP_SPECIFIED_NUM_NODES_CASE_FILE = os.path.join(os.path.dirname(self.test_cumulus_config),
                                                               "skip_specified_num_nodes_case")
        self.NO_EMON_FOUND_FILE = os.path.join(os.path.dirname(self.test_cumulus_config), "no_emon_found")
        self.TIMEOUT_WAIT_FOR_SERVER_FILE = os.path.join(os.path.dirname(self.test_cumulus_config),
                                                         "timout_wait_for_server")
        self.CLUSTER_HW_CONFIG = os.path.join(os.path.dirname(self.test_cumulus_config), "cluster_config")

    def update_cumulus(self):
        # for cumulus container clean up
        with open(os.path.join(os.getenv("WORKSPACE", ""), "run_uri"), "a+") as fd:
            fd.write(run_uri)
        # get required cluster info
        with open(self.CLUSTER_CONFIG, "rt") as fd:
            required_cluster = yaml.safe_load(fd)
        # only support single node first due to limited systems

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

        cloud_validation = False
        return_code = 0

        # get cluster type
        log_folder = self.test_cumulus_config.split("/")[-2]
        cluster_type = log_folder.split("-")[1].split("_")[0]
        sut_type = self.platform

        if cluster_type == 'baremetal' or cluster_type == 'snc4':
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

        test_case_name = self.test_cumulus_config.split('/')[-2]
        test_case_name = test_case_name.replace("logs-", '')

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

        registry = ''
        required_worker_available = False
        required_worker_exists = False
        timeout_count_max = 5  # total 10 mins
        timeout_count = 0
        cluster_workers = []
        logging.info("need to run on specified hw")
        register_cluster_id = ''
        this_job_register_cluster = False
        while True:
            if timeout_count < timeout_count_max:
                available_cluster_count = 0
                controller_ip_not_reachable_cluster_count = 0
                worker_ip_not_reachable_cluster_count = 0
                worker_other_mismatch_cluster_count = 0
                # check if required workers are available
                for cluster in clusters[platform]:
                    if required_worker_available is True:
                        break
                    cluster_controller = {}
                    cluster_workers = []
                    info = sorted(cluster.values())[0]
                    available_server_count = 0
                    # special logic for CDN-NGINX workload
                    if self.WORKLOAD != 'CDN-NGINX' and "cdn-only" in info.keys():
                        continue
                    # check if this case have already booked the cluster part of servers
                    cluster_id = ''.join(cluster.keys()).replace('cluster', '')
                    # if register_cluster_id != '' and register_cluster_id != cluster_id:
                    #     logging.info(
                    #         "This job has been registered other cluster and it is not current cluster, toggle next cluster...")
                    #     continue
                    if 'master' in info.keys():
                        pass
                    else:
                        logging.info("master is not defined in cluster, please fix......")
                        continue
                    if len(info['workers']) >= required_worker_number or len(info['workers']) < required_worker_number:
                        # # check hw config match or not
                        # cluster_worker_hw_list = []
                        # for server in info['workers']:
                        #     worker = sorted(server.values())[0]
                        #     cluster_worker_hw_list.append(str(worker['hw_config']))
                        # if str(run_hw_config) not in cluster_worker_hw_list:
                        #     logging.info("Cluster%s does not have worker that hw config is %s, next cluster ..." % (cluster_id, run_hw_config))
                        #     continue
                        # else:
                        #     logging.info("Cluster%s has worker(s) match the hw config %s" % (cluster_id, run_hw_config))
                        # check controller
                        controller_ip = info['master']['ip']
                        controller_user = info['master']['user']
                        controller_port = info['master']['port']
                        logging.info("ssh -p %s %s@%s 'ls /tmp' > /dev/null" %
                                     (controller_port, controller_user, controller_ip))
                        if os.system("ssh -p %s %s@%s 'ls /tmp' > /dev/null" %
                                     (controller_port, controller_user, controller_ip)) == 0:
                            cluster_controller['ip'] = controller_ip
                            cluster_controller['user'] = controller_user
                            cluster_controller['port'] = controller_port
                        else:
                            # if controller is not online, skip to next cluster， need enhance if ip not works.
                            logging.info("controller %s is not reachable, will try again......" % controller_ip)
                            controller_ip_not_reachable_cluster_count = controller_ip_not_reachable_cluster_count + 1
                            continue
                        # if cluster_id == register_cluster_id:
                        #     i = i
                        #     logging.info(
                        #         "Currently cluster %s server(s) have been registered for this case" % i)
                        # else:
                        #     i = 0
                        available_cluster_count = available_cluster_count + 1
                        # if required_worker_number >= 2:
                        #     master_ip = info['master']['ip']
                        #     zks = ZKState("/usr/zookeeper/tmp")
                        #     children = zks.list_children()
                        #     zks.close()
                        #     cur_for_multi_wl_node_num = 0
                        #     for child in children:
                        #         if "%s_cluster_%s" % (platform, master_ip) in child:
                        #             cur_for_multi_wl_node_num = cur_for_multi_wl_node_num + int(child.split("_")[-1].split(".")[0])
                        #     cur_free_multi_wl_node_num = len(info['workers']) - cur_for_multi_wl_node_num
                        #     # limit multi-node cluster workloads can reserved cluster servers number at the same time, queue if more than
                        #     if (cur_for_multi_wl_node_num + required_worker_number) <= len(info['workers']) and not this_job_register_cluster:
                        #         logging.info("Current cluster for multiple workload node(s) register num is %s/%s, free %s" %
                        #                 (cur_for_multi_wl_node_num, len(info['workers']), cur_free_multi_wl_node_num))
                        #         this_job_lock = "%s_cluster_%s_%s_%s" % (platform, master_ip, run_uri, required_worker_number)
                        #         zks = ZKState("/usr/zookeeper/tmp", this_job_lock)
                        #         # stagger concurrent time when get cluster locker
                        #         sleeptime=random.randint(1, 3)
                        #         time.sleep(sleeptime)
                        #         if zks.process_start():
                        #             logging.info("%s cluster register successfully!" % this_job_lock)
                        #             this_job_register_cluster = True
                        #             register_cluster_id = ''.join(cluster.keys()).replace('cluster', '')
                        #             check_zks = ZKState("/usr/zookeeper/tmp")
                        #             children = check_zks.list_children()
                        #             check_zks.close()
                        #             cur_for_multi_wl_node_num = 0
                        #             for child in children:
                        #                 if "%s_cluster_%s" % (platform, master_ip) in child:
                        #                     cur_for_multi_wl_node_num = cur_for_multi_wl_node_num + int(
                        #                         child.split("_")[-1].split(".")[0])
                        #             if cur_for_multi_wl_node_num > len(info['workers']):
                        #                 zks.process_end()
                        #                 logging.info(
                        #                     "Cluster %s register nodes number is %s, more than maximum support for reserved, waiting ..." % (cluster_id, cur_for_multi_wl_node_num))
                        #                 register_cluster_id = ''
                        #                 this_job_register_cluster = False
                        #                 continue
                        #     elif cluster_id == register_cluster_id:
                        #         logging.info("The cluster is reserved, waiting for idle server")
                        #     else:
                        #         logging.info("Current multi-node workload to reach the maximum number supported by the cluster_id: %s, waiting ..." % cluster_id)
                        #     if cluster_id != register_cluster_id:
                        #         continue
                        i = 0
                        for server in info['workers']:
                            worker = sorted(server.values())[0]
                            ip_reachable = True
                            ip = worker['ip']
                            ssh_port = worker['port']
                            ssh_user = worker['user']
                            # zk_path = "/usr/zookeeper/tmp"
                            # check server is reachable or not
                            if os.system("ssh -p %s %s@%s 'ls /tmp' > /dev/null" %
                                         (ssh_port, ssh_user, ip)) == 0:
                                logging.info("current HW config is %s" % ip)
                                cluster_workers.append(worker)
                                i = i + 1
                                logging.info("Required worker number %d" % required_worker_number)
                                logging.info("Worker number %d" % i)
                                if i == required_worker_number:
                                    required_worker_available = True
                                    with open(self.CLUSTER_HW_CONFIG, "w") as fd:
                                        fd.write(worker['hw_config'])
                                    registry = info['docker_registry']
                                    break
                                # if str(worker['hw_config']) == str(run_hw_config):
                                # logging.info("previous ip is %s" %worker['ip'])
                                # available_server_count = available_server_count + 1
                                # required_worker_exists = True
                                # zks = ZKState(zk_path, ip)
                                # if not zks.processing():
                                # logging.info("%s is free :" % ip)
                                # if zks.process_start():
                                # logging.info("%s is added to queue" % ip)
                                # cluster_workers.append(worker)
                                # i = i + 1
                                # benchmark_zk_path = "/usr/zookeeper/benchmark"
                                # ip_and_build = ip + '_' + build_id
                                # benchmark_zks = ZKState(benchmark_zk_path, ip_and_build)
                                # benchmark_zks.process_start()
                                # if i == required_worker_number:
                                # required_worker_available = True
                                # os.system("echo %s > %s" % (
                                # worker['hw_config'], self.CLUSTER_HW_CONFIG))
                                # registry = info['docker_registry']
                                # break
                                # else:
                                # logging.info("other job wins the server, waiting...")
                                # zks.close()
                                # else:
                                # check_benchmark_zks = ZKState("/usr/zookeeper/benchmark")
                                # benchmark_children = check_benchmark_zks.list_children()
                                # check_benchmark_zks.close()
                                # job_id = '0000'
                                # for child in benchmark_children:
                                # if ip in child:
                                # job_id = child.split("_")[-1].split(".")[0]
                                # logging.info("%s is under validation, it is used by job id: %s" % (ip, job_id))
                                # zks.close()
                            else:
                                # need enhance if server is down all the time...
                                ip_reachable = False
                                logging.info("%s is unreachable. :" % ip)
                        if available_server_count == 0 and required_worker_exists is False:
                            if ip_reachable is False:
                                worker_ip_not_reachable_cluster_count = worker_ip_not_reachable_cluster_count + 1
                            else:
                                worker_other_mismatch_cluster_count = worker_other_mismatch_cluster_count + 1
                    else:
                        continue
                required_worker_available = True
                if required_worker_available is True:
                    logging.info("already found matched server, continue testing......")
                    break
                # if all available cluster's controller can't be reached, then loop 10 mins
                if available_cluster_count == controller_ip_not_reachable_cluster_count or available_cluster_count == worker_ip_not_reachable_cluster_count:
                    timeout_count = timeout_count + 1
                if available_cluster_count == 0:
                    logging.info("no cluster has a sufficient number of workers")
                    os.mknod(self.NO_ENOUGH_WORKERS_CLUSTER_FILE)
                    sys.exit(3)
                    break
                if available_cluster_count == worker_other_mismatch_cluster_count:
                    logging.info("no matched server found, exit........")
                    os.mknod(self.NO_LABEL_FOUND_FILE)
                    sys.exit(3)
                    break
                else:
                    time.sleep(120)
            else:
                logging.info("timeout wait for available work ready, exit......")
                os.mknod(self.TIMEOUT_WAIT_FOR_SERVER_FILE)
                sys.exit(3)
                break

        # load cumulus-config
        logging.info("======================================")
        logging.info(cluster_controller)
        logging.info(cluster_workers)
        logging.info("======================================")
        with open(self.test_cumulus_config, "rt") as fd:
            cumulus_config = yaml.safe_load(fd)

        if required_worker_available is True:
            controller = {}
            controller['ip_address'] = cluster_controller['ip']
            controller['user_name'] = cluster_controller['user']
            controller['ssh_private_key'] = "/home/.ssh/id_rsa"
            controller['internal_ip'] = cluster_controller['ip']
            controller['ssh_port'] = cluster_controller['port']
            controller['install_packages'] = False
            controller['os_type'] = "centos8"

            cumulus_config['docker_pt']['vm_groups']['worker']['vm_count'] = len(cluster_workers)

            if "controller" not in cumulus_config['docker_pt']['vm_groups'].keys():
                cumulus_config['docker_pt']['vm_groups']['controller'] = {}
            cumulus_config['docker_pt']['vm_groups']['controller']['static_vms'] = []
            cumulus_config['docker_pt']['vm_groups']['controller']['static_vms'].append(controller)

            cumulus_config['docker_pt']['vm_groups']['worker']['static_vms'] = []

            for server in cluster_workers:
                worker = {}
                worker['ip_address'] = server['ip']
                worker['user_name'] = server['user']
                worker['ssh_private_key'] = "/home/.ssh/id_rsa"
                worker['internal_ip'] = server['ip']
                worker['ssh_port'] = server['port']
                worker['install_packages'] = False
                worker['os_type'] = "centos8"
                # clean up collectd first
                # clean_collectd_and_namespace(cluster_controller['ip'], cluster_controller['user'],cluster_controller['port'], server['ip'], server['user'],server['port'])
                cumulus_config['docker_pt']['vm_groups']['worker']['static_vms'].append(worker)
                if "intel_publisher_sut_machine_type" in cumulus_config['docker_pt']['flags'].keys():
                    cumulus_config['docker_pt']['flags']["intel_publisher_sut_machine_type"] = sut_type
                    cumulus_config['docker_pt']['flags'][
                        'intel_publisher_sut_metadata'] = "CPU:%s,Memory:%s,PCH:%s,IFWI:%s,OS:%s,Kernel:%s,Kubernetes:%s,Docker:%s" % (
                        server['hw_info']['CPU'], server['hw_info']['Memory'], server['hw_info']['PCH'],
                        server['hw_info']['IFWI'], server['hw_info']['OS'], server['hw_info']['Kernel'],
                        server['hw_info']['Kubernetes'], server['hw_info']['Docker'])
                else:
                    cumulus_config['docker_pt']['flags'][
                        'dpt_params'] = "CPU:%s,Memory:%s,PCH:%s,IFWI:%s,OS:%s,Kernel:%s,Kubernetes:%s,Docker:%s" % (
                        server['hw_info']['CPU'], server['hw_info']['Memory'], server['hw_info']['PCH'],
                        server['hw_info']['IFWI'], server['hw_info']['OS'], server['hw_info']['Kernel'],
                        server['hw_info']['Kubernetes'], server['hw_info']['Docker'])
            cumulus_config['docker_pt']['flags']['dpt_registry_map'] = "0.0.0.0:5000->{0}".format(registry)
            if re.search(r"\s", cumulus_config['docker_pt']['flags']['dpt_script_args']):
                cumulus_config['docker_pt']['flags']['dpt_script_args'] = "'%s'" % cumulus_config['docker_pt']['flags'][
                    'dpt_script_args']

            with open(self.test_cumulus_config, 'w+', encoding='utf-8') as file:
                cumulus_config_info = yaml.safe_dump(cumulus_config, default_flow_style=False)
                cumulus_config_info = cumulus_config_info.replace("'''", "\"")
                cumulus_config_info = cumulus_config_info.replace("'", "\"")
                file.write(cumulus_config_info)

            # run pkb.py
            cmd = ["python3", "/PerfKitBenchmarker/pkb.py", "--ip_addresses=EXTERNAL", "--trace_skip_cleanup",
                   "--trace_skip_install",
                   "--trace_vm_groups=worker", "--trace_allow_benchmark_control"
                   ]
            cumulus_options_list = self.cumulus_option.split(" ")
            cmd.extend(cumulus_options_list)

            other_parameters = [f"--run_uri={self.run_uri}",
                                f"--temp_dir={self.tmp_dir}", "--benchmarks=docker_pt",
                                f"--benchmark_config_file={self.test_cumulus_config}",
                                "--ignore_package_requirements"
                                ]
            cmd.extend(other_parameters)
            logging.info(str(cmd))
            p = subprocess.Popen(
                cmd,
                shell=False,
                cwd=os.path.dirname(self.test_cumulus_config),
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
            return_code = p.returncode
        sys.exit(return_code)


if __name__ == '__main__':
    test_cluster_config = sys.argv[1]
    test_cumulus_config = sys.argv[2]
    run_uri = sys.argv[3]
    tmp_dir = sys.argv[4]
    cumulus_option = sys.argv[5]
    gated = sys.argv[6]

    provision = Provision(test_cumulus_config, test_cluster_config, run_uri, tmp_dir, cumulus_option, gated)
    provision.update_cumulus()
