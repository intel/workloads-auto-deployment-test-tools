#!/usr/bin/python3
import time
import os
import logging
import yaml
import sys
import json
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Master(yaml.YAMLObject):
    def __init__(self, ip, user, port=22):
        self.ip = ip
        self.port = port
        self.user = user


class Worker(yaml.YAMLObject):
    def __init__(self, name, ip, internal_ip, user, hw_config, hw_info, labels, port=22):
        self.ip = ip
        if internal_ip:
            self.internal_ip = internal_ip
        self.port = port
        self.user = user
        self.hw_config = hw_config
        self.hw_info = hw_info
        self.labels = labels


class Cluster(yaml.YAMLObject):
    def __init__(self):
        self.config = {}

    def set_config(self, master, worker_list, platform, registry):
        self.config[platform] = [
            {"cluster": {"workers": worker_list, "master": master, 'docker_registry': registry, 'location': 'GDC'}}]

    def get_config(self):
        return self.config


def noop(self, *args, **kw):
    pass


if __name__ == '__main__':
    master_ip = sys.argv[1]
    workers_ip = sys.argv[2].split(",")
    platform = sys.argv[3]
    get_instance_api = sys.argv[4]
    registry = sys.argv[5]
    master_info = {}
    workers_info = []

    response = requests.get(
        url=get_instance_api, verify="/home/cert.pem")
    machines = response.json()
    for machine in machines:
        # print(machine)
        if machine['ip'] == master_ip:
            master_info = machine
        for worker_ip in workers_ip:
            if worker_ip == machine['ip']:
                workers_info.append(machine)
    master = Master(master_ip, master_info['username'])
    workers = []
    count = 1
    for worker_info in workers_info:
        worker_name = "worker" + str(count)
        hw_config = "2"
        hw_info = {
            'CPU': 'SPR E0 Q0A9 48cores 2S 1.8G HT-Enabled1',
            'Memory': 'DDR5 4000 16G*32',
            'PCH': 'EBG B1 QYKV',
            'IFWI': 'EGSDCRB1.86B.0075.D01.2202211157',
            'OS': 'CentOS Stream release 8',
            'Kernel': '5.15.0-spr.bkc.pc.2.10.0.x86_64',
            'Kubernetes': 'v1.21.1',
            'Docker': '20.10.12',
            'Microcode': '0x8e0002a0',
            'PCIE': 'GEN5',
            'NIC': 'Ethernet Controller E810-C for QSFP',
            'BOOT': 'INTEL SSD',
            'Platform': '2S Archer City',
        }
        worker = Worker('test', worker_info['ip'], worker_info['internal_ip'], worker_info['username'], hw_config, hw_info, worker_info['labels'], worker_info['ssh_port'])
        workers.append({worker_name: worker})
        count = count + 1

    cluster = Cluster()
    cluster.set_config(master, workers, platform, registry)
    yaml.emitter.Emitter.process_tag = noop
    CLUSTER_FILE = os.path.join(os.getenv("WORKSPACE", ""), "pool", "cluster.yaml")
    fd = open(CLUSTER_FILE, "w")

    print(yaml.dump(cluster.get_config(), fd, default_flow_style=False, allow_unicode=False))
    fd.close

