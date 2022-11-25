#!/usr/bin/python3
from result import Execution
import subprocess
import time
import os
import re
import logging
import sys
import yaml
from utils import workload_params_to_yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
SCRIPT_PATH = os.path.join(os.getenv("WORKSPACE",""), 'script/jenkins/script')

def updateCommit(commit):
    return re.match(r"\w+", commit).group()

def run_benchmark(session, workload, platform, gated, commit):
    return_code = 0

    workload_params = os.getenv('workload_params', '')
    workload_params_to_yaml(workload_params)
    timeout = os.getenv("timeout","")
    
    commit =  updateCommit(commit)
    cmd = "%s/workload.sh prepare %s %s && %s/workload.sh benchmark %s Single" % (
        SCRIPT_PATH, timeout, commit, SCRIPT_PATH, workload)
    logging.info(cmd)
    p = subprocess.Popen(
        cmd,
        shell=True,
        cwd=SCRIPT_PATH,
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

def create_artifacts(session, workload, platform, gated):
    final_config = ''
    if gated == 'false':
        #create artifacts
        cmd = "%s/workload.sh artifacts %s" % (SCRIPT_PATH, workload)
        logging.info(cmd)
        p = subprocess.Popen(
            cmd,
            shell=True,
            cwd=SCRIPT_PATH,
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
        # generate execution info
        benchmark_execution = Execution()
        benchmark_execution.generate_benchmark_execution_info(session, platform, workload, final_config)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        logging.error("You must specify session and action")
        sys.exit(1)
    session = sys.argv[1]
    items = session.split('_')
    commit = session.split('_')[-1]
    gated = os.getenv("gated", "false")
    action = sys.argv[2]
    if action.lower() == 'benchmark':
        run_benchmark(session, os.getenv("workload",""), os.getenv("platform",""), gated, commit)
    elif action.lower() == 'artifacts':
        create_artifacts(session, os.getenv("workload",""), os.getenv("platform",""), gated)

