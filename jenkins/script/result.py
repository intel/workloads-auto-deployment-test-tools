import json
import os
import re
import requests, datetime
import yaml
from utils import sha256, execute_cmd, get_platforms
import subprocess # nosec
import pathlib
import operator
from urllib.parse import urlparse

class Execution(object):
    def __init__(self):
        pass

    def check_result_exist(self, test_result_folder):
        '''
        check test result json exist or not, if yes, check the run_count
        :param test_result_folder:
        :return:
        '''
        json_file = os.path.join(test_result_folder, 'execution.json')
        if os.path.exists(json_file):
            benchmark_runs = os.listdir(test_result_folder)
            with open(json_file, 'r') as fp:
                execution = json.load(fp)
                if 'run_count' in execution.keys():
                    if execution['run_count'] == len(benchmark_runs) - 1:
                        return True
                    else:
                        return False
                else:
                    return True
        else:
            return False

    def generate_benchmark_execution_info(self, session_id, platform, workload, config):
        '''
        generate test result for each benchmark run
        :param platform:
        :param workload:
        :param config:
        :return: benchmark_execution_info dict
        '''
        benchmark_execution_info = {}
        benchmark_execution_info['execution'] = {}
        build_id = os.getenv("BUILD_ID","")
        performance = os.getenv("performance", 'false')
        items = session_id.split('_')
        test_config = os.getenv("workload_test_config_yaml", '')
        test_config = test_config if test_config else 'default'

        if len(items) == 5:
            wiki_platform_commit = items[-2]
        else:
            wiki_platform_commit = 'master'

        test_result_folder = os.path.join(os.getenv("WORKSPACE",""), "result")
        customer = os.getenv('customer', 'main')
        art_url = os.getenv("artifactory_url","")
        art_host = urlparse(art_url).netloc
        if customer == 'ali':
            art_log_url = 'https://af01p-sh.devtools.intel.com/artifactory/platform_hero_ali-sh-local/auto_provision/%s/%s_%s_%s/logs' % (
                session_id, platform, workload, build_id)
            ctest_folder = os.path.join(os.getenv("WORKSPACE",""), 'validation/build/workload/customer/ali', workload, 'Testing/Temporary')
        elif customer == 'tencent':
            art_log_url = 'https://af01p-sh.devtools.intel.com/artifactory/platform_hero_tencent-sh-local/auto_provision/%s/%s_%s_%s/logs' % (
                session_id, platform, workload, build_id)
            ctest_folder = os.path.join(os.getenv("WORKSPACE",""), 'validation/build/workload/customer/tencent', workload, 'Testing/Temporary')
        else:
            
            art_log_url = 'http://%s/ui/native/auto_provision/%s/%s_%s_%s/logs' % (
                art_host, session_id, platform, workload, build_id)
            ctest_folder = os.path.join(os.getenv("WORKSPACE",""), 'validation/build/workload', workload, 'Testing/Temporary')
        execution_json = 'http://%s/ui/native/auto_provision/%s/execution/%s_%s_%s.json' % (
                art_host, session_id, platform, workload, build_id)

        # check test case details from ctest folder, pass/fail
        failed_test_case = []
        #If test was aborted, the test log file name end with .tmp
        failed_test_log = os.path.join(ctest_folder, "LastTestsFailed.log")
        if not os.path.exists(failed_test_log):
            failed_test_log = os.path.join(ctest_folder, "LastTestsFailed.log.tmp")
        all_test_log = os.path.join(ctest_folder, "LastTest.log")
        if not os.path.exists(all_test_log):
            all_test_log = os.path.join(ctest_folder, "LastTest.log.tmp")
        if os.path.exists(failed_test_log):
            with open(failed_test_log, 'r') as fl:
                for line in fl:
                    failed_case_name = line.strip("\n").split(":")[1]
                    failed_test_case.append(failed_case_name)

        # get all test case info
        if os.path.exists(all_test_log):
            with open(all_test_log, 'r') as all:
                for line in all:
                    if "Testing:" in line:
                        # for cloud case, case name is test_aws-machine-type_case
                        case_name = line.strip("\n").split(" ")[2]
                        cluster_type = case_name.split("_")[1]
                        if '-' in cluster_type:
                            cluster_type = cluster_type.split("-")[0]
                        logs_folder_name = "logs-" + case_name.split("test_")[-1]
                        test_platform = platform + '_' + cluster_type.upper()
                        if cluster_type == 'baremetal' or cluster_type == 'static':
                            test_platform = platform
                        if cluster_type in ['aws', 'gcp', 'azure']:
                            test_platform = platform + '_' + cluster_type.upper()
                        if cluster_type.lower() == 'gaudi':
                            test_platform = platform + '_AWS'
                        if cluster_type.lower() == 'inf':
                            test_platform = platform + '_AWS'
                        if cluster_type.lower() == 't4':
                            test_platform = platform + '_AWS'
                        if test_platform not in benchmark_execution_info['execution']:
                            benchmark_execution_info['execution'][test_platform] = {}
                            benchmark_execution_info['execution'][test_platform][workload] = {}
                            benchmark_execution_info['execution'][test_platform][workload]['kpi'] = {}
                            benchmark_execution_info['execution'][test_platform][workload]['bom'] = {}
                            benchmark_execution_info['execution'][test_platform][workload]['Total'] = 0
                            benchmark_execution_info['execution'][test_platform][workload]['Passed'] = 0
                            benchmark_execution_info['execution'][test_platform][workload]['Failed'] = 0
                            benchmark_execution_info['execution'][test_platform][workload]['Blocked'] = 0
                            benchmark_execution_info['execution'][test_platform][workload]['Attempted'] = 0
                            benchmark_execution_info['execution'][test_platform][workload]['No_Run'] = 0
                            benchmark_execution_info['execution'][test_platform][workload]['all_test_case'] = []
                            benchmark_execution_info['execution'][test_platform][workload]['passed_test_case'] = []
                            benchmark_execution_info['execution'][test_platform][workload]['failed_test_case'] = []
                            benchmark_execution_info['execution'][test_platform][workload]['no_run_test_case'] = []
                        benchmark_execution_info['execution'][test_platform][workload]['Total'] = \
                            benchmark_execution_info['execution'][test_platform][workload]['Total'] + 1
                        benchmark_execution_info['execution'][test_platform][workload]['Attempted'] = \
                            benchmark_execution_info['execution'][test_platform][workload]['Attempted'] + 1

                        benchmark_execution_info['execution'][test_platform][workload]['log_url'] = art_log_url
                        benchmark_execution_info['execution'][test_platform][workload]['machine_config'] = config
                        benchmark_execution_info['execution'][test_platform][workload]['execution_json'] = execution_json

                        benchmark_execution_info['execution'][test_platform][workload]['all_test_case'].append(
                            case_name)

                        # no_label_case as no_run case
                        label_not_found_file = os.path.join(test_result_folder, logs_folder_name, 'no_label_found')
                        emon_not_found_file = os.path.join(test_result_folder, logs_folder_name, 'no_emon_found')
                        timeout_wait_for_server_file = os.path.join(test_result_folder, logs_folder_name,
                                                                    'timout_wait_for_server')
                        no_enough_workers_cluster_file = os.path.join(test_result_folder, logs_folder_name,
                                                                    'no_enough_workers_cluster')
                        skip_specified_num_nodes_case_file = os.path.join(test_result_folder, logs_folder_name,
                                                                    'skip_specified_num_nodes_case')

                        if os.path.exists(label_not_found_file) or os.path.exists(
                                emon_not_found_file) or os.path.exists(
                                timeout_wait_for_server_file) or os.path.exists(
                                no_enough_workers_cluster_file) or os.path.exists(skip_specified_num_nodes_case_file):
                            benchmark_execution_info['execution'][test_platform][workload][
                                'no_run_test_case'].append(case_name)
                            benchmark_execution_info['execution'][test_platform][workload]['No_Run'] = \
                                benchmark_execution_info['execution'][test_platform][workload]['No_Run'] + 1
                            benchmark_execution_info['execution'][test_platform][workload]['Attempted'] = \
                                benchmark_execution_info['execution'][test_platform][workload]['Attempted'] - 1
                        else:
                            if case_name in failed_test_case:
                                benchmark_execution_info['execution'][test_platform][workload][
                                    'failed_test_case'].append(case_name)
                                benchmark_execution_info['execution'][test_platform][workload]['Failed'] = \
                                    benchmark_execution_info['execution'][test_platform][workload]['Failed'] + 1
                            else:
                                benchmark_execution_info['execution'][test_platform][workload][
                                    'passed_test_case'].append(
                                    case_name)
                                benchmark_execution_info['execution'][test_platform][workload]['Passed'] = \
                                    benchmark_execution_info['execution'][test_platform][workload]['Passed'] + 1

        # get kpi info
        for root, dirs, files in os.walk(os.path.join(test_result_folder)):
            if "pkb.log" in files or "tfplan.logs" in files:
                folder_name = os.path.basename(root)
                folder_list = root.split("/")
                for folder in folder_list:
                    if 'logs-' in folder:
                        folder_name = folder
                benchmark_list = folder_name.split('logs-')
                if len(benchmark_list) == 1:
                    benchmark_name = workload
                    test_name = workload.lower()
                else:
                    benchmark_name = benchmark_list[1]
                    test_name = benchmark_name
                cluster_type = test_name.split("_")[0]
                # for cloud case, case name is test_aws-machine-type_case
                if '-' in cluster_type:
                    cluster_type = cluster_type.split("-")[0]

                # get workload_params from cumulus-config.yaml
                case_log_folder = root.split('runs')[0]
                f = open("%s/workload-config.yaml" % root, 'r')
                result = f.read()
                case_workload_config = yaml.safe_load(result)
                case_sha256 = sha256(case_workload_config['tunables'])

                test_platform = platform + '_' + cluster_type.upper()
                if cluster_type == 'baremetal' or cluster_type == 'static':
                    test_platform = platform
                if cluster_type in ['aws', 'gcp', 'azure']:
                    test_platform = platform + '_' + cluster_type.upper()
                if cluster_type.lower() == 'gaudi':
                    test_platform = platform + '_AWS'
                if cluster_type.lower() == 'inf':
                    test_platform = platform + '_AWS'
                if cluster_type.lower() == 't4':
                    test_platform = platform + '_AWS'
                if test_platform not in benchmark_execution_info['execution']:
                    benchmark_execution_info['execution'][test_platform] = {}
                    benchmark_execution_info['execution'][test_platform][workload] = {}
                    benchmark_execution_info['execution'][test_platform][workload]['kpi'] = {}
                    benchmark_execution_info['execution'][test_platform][workload]['bom'] = {}
                    benchmark_execution_info['execution'][test_platform][workload]['Total'] = 0
                    benchmark_execution_info['execution'][test_platform][workload]['Passed'] = 0
                    benchmark_execution_info['execution'][test_platform][workload]['Failed'] = 0
                    benchmark_execution_info['execution'][test_platform][workload]['Blocked'] = 0
                    benchmark_execution_info['execution'][test_platform][workload]['Attempted'] = 0
                    benchmark_execution_info['execution'][test_platform][workload]['No_Run'] = 0
                    benchmark_execution_info['execution'][test_platform][workload]['all_test_case'] = []
                    benchmark_execution_info['execution'][test_platform][workload]['passed_test_case'] = []
                    benchmark_execution_info['execution'][test_platform][workload]['failed_test_case'] = []
                    benchmark_execution_info['execution'][test_platform][workload]['no_run_test_case'] = []
                pkb_log = os.path.join(root, 'pkb.log')
                if os.path.exists("%s/intel_publisher/perfKitRuns.json" % root):
                    with open("%s/intel_publisher/perfKitRuns.json" % root, 'r') as fp:
                        run_details = json.load(fp)
                    run_uri = run_details['uri']
                else:
                    run_uri = ''

                cmd = "cat %s | grep 'End to End Runtime' | grep seconds | awk '{print $5}'" % pkb_log
                ret, output = execute_cmd(cmd)
                test_time = output.decode('ascii').strip().split('\n')
                if len(test_time) > 0:
                    execution_time = test_time[0]
                else:
                    execution_time = ''

                if test_name not in benchmark_execution_info['execution'][test_platform][workload]['kpi'].keys():
                    benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name] = {}
                    benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name]['metrics'] = {}
                cumulus_url = "https://cumulus-dashboard.intel.com/services-framework/run_uri/%s" % run_uri
                #benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name][
                #    'cumulus_url'] = cumulus_url
                benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name][
                    'test_time'] = execution_time
                benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name]['sha256'] = case_sha256
                # get hw config
                hw_config_file = os.path.join(test_result_folder, folder_name, 'cluster_config')

                if os.path.exists(hw_config_file):
                    with open(hw_config_file, 'r') as fl:
                        hw_config = fl.read().split("\n")[0]
                else:
                    hw_config = '0'

                cumulus_config = os.path.join(test_result_folder, folder_name, 'cumulus-config.yaml')
                benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name]['config'] = hw_config
                benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name]['test_config'] = test_config
                benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name][
                    'wiki_platform_version'] = wiki_platform_commit

                # add all kpi
                # kpi_log_name = "kpi_*%s.log" % (benchmark_name.lower())
                kpi_log_name = "kpi_*%s.log" % (benchmark_name)
                kpi_log = os.path.join(test_result_folder, "kpi/%s" % kpi_log_name)
                all_metrics_cmd = "cat %s" % (str(kpi_log))
                if performance == 'true':
                    benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name]['itr'] = {}
                ret_code, metrics_info = execute_cmd(all_metrics_cmd)
                metrics = metrics_info.decode('ascii').strip().split('\n')

                for metric in metrics:
                    if metric.startswith('*'):
                        info = metric.split(':')
                        metric_name = info[0].replace('*', '')
                        benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name]['metrics'][
                            metric_name] = info[1]
                    else:
                        if performance == 'true':
                            if 'itr' in metric.split(' ')[0]:
                                itr = metric.split(' ')[0]
                                if ':' not in metric:
                                    itr_value = ' '
                                else:
                                    itr_value = metric.split(':')[1]
                                benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name]['itr'][itr] = itr_value

                # case return fail if no kpi
                if not bool(
                        benchmark_execution_info['execution'][test_platform][workload]['kpi'][test_name]['metrics']):
                    real_case_name = 'test_' + test_name
                    if real_case_name in benchmark_execution_info['execution'][test_platform][workload][
                        'passed_test_case']:
                        benchmark_execution_info['execution'][test_platform][workload]['passed_test_case'].remove(
                            real_case_name)
                        benchmark_execution_info['execution'][test_platform][workload]['failed_test_case'].append(
                            real_case_name)
                        benchmark_execution_info['execution'][test_platform][workload]['Failed'] = \
                            benchmark_execution_info['execution'][test_platform][workload]['Failed'] + 1
                        benchmark_execution_info['execution'][test_platform][workload]['Passed'] = \
                            benchmark_execution_info['execution'][test_platform][workload]['Passed'] - 1
                        os.system(
                            "echo %s >> %s/logs/ctest/LastTestsFailed.log" % (real_case_name, os.getenv("WORKSPACE","")))
        #if test failed with no pkb.log, also mark it as failed
        for item in os.listdir(test_result_folder):
            if os.path.isdir(item) and item.startswith('logs-'):
                test_dir = os.path.join(test_result_folder,item)
                # if not find pkb.log
                if not sorted(pathlib.Path(test_dir).glob('**/pkb.log')):
                    test_name = item.replace('logs-','')
                    cluster_type = test_name.split("_")[0]
                    if '-' in cluster_type:
                        cluster_type = cluster_type.split("-")[0]
                    test_platform = platform + '_' + cluster_type.upper()
                    if cluster_type == 'baremetal' or cluster_type == 'static':
                        test_platform = platform
                    if cluster_type in ['aws', 'gcp', 'azure']:
                        test_platform = platform + '_' + cluster_type.upper()
                    if cluster_type.lower() == 'gaudi':
                        test_platform = platform + '_AWS'
                    real_case_name = 'test_' + test_name
                    if real_case_name in benchmark_execution_info['execution'][test_platform][workload]['passed_test_case']:
                        benchmark_execution_info['execution'][test_platform][workload]['passed_test_case'].remove(
                            real_case_name)
                        benchmark_execution_info['execution'][test_platform][workload]['failed_test_case'].append(
                            real_case_name)
                        benchmark_execution_info['execution'][test_platform][workload]['Failed'] = \
                            benchmark_execution_info['execution'][test_platform][workload]['Failed'] + 1
                        benchmark_execution_info['execution'][test_platform][workload]['Passed'] = \
                            benchmark_execution_info['execution'][test_platform][workload]['Passed'] - 1
                        os.system(
                            "echo %s >> %s/logs/ctest/LastTestsFailed.log" % (real_case_name, os.getenv("WORKSPACE","")))
        # get bom info
        bom_folder = os.path.join(test_result_folder, "bom")
        if os.path.exists(bom_folder):
            for bom_file in os.listdir(bom_folder):
                bom = os.path.join(bom_folder, bom_file)
                with open(bom) as file:
                    for line in file:
                        line = line.rstrip("\n")
                        bom_name = line.split(' ')[0]
                        bom_value = line.split(' ')[1]
                        benchmark_execution_info['execution'][test_platform][workload]['bom'][bom_name] = bom_value
        print(benchmark_execution_info)
        return benchmark_execution_info

    def store_benchmark_execution_info(self, benchmark_execution_info, front_job_id, platform, workload, store_url):
        '''
        store test result for each benchmark run
        :param benchmark_execution_info: dict
        :param front_job_id: str
        :param platform
        :param workload
        :param store_url
        :return:
        '''
        if ({'execution': {}} == benchmark_execution_info):
            print("Execution result is null...")
            return 0

        json_str = json.dumps(benchmark_execution_info, indent=4)
        execution_json_file = os.path.join(os.getenv("WORKSPACE",""), "%s_%s.json" % (platform, workload))
        with open('%s' % execution_json_file, 'w') as json_file:
            json_file.write(json_str)

        dict_info_execution = benchmark_execution_info
        result_to_store_list = []
        result_to_store = {}
        dict_info_execution_key = list(dict_info_execution.keys())[0]
        result_to_store['job_id'] = front_job_id
        dict_info_platform, result_to_store['platform'] = self.get_inner_key_from_dict(dict_info_execution, 'execution')
        dict_info_workload, result_to_store['workload'] = self.get_inner_key_from_dict(dict_info_platform, result_to_store['platform'])
        dict_info_kpis_and_others, kpis_and_others = self.get_inner_key_from_dict(dict_info_workload, result_to_store['workload'])
        dict_info_kpis = dict_info_kpis_and_others['kpi']

        portal_username = subprocess.run(['vault', 'kv', 'get', '-mount=kv', '-field=portalUserName', 'wsf-secret-password'], capture_output=True, text=True).stdout
        portal_password = subprocess.run(['vault', 'kv', 'get', '-mount=kv', '-field=portalPassword', 'wsf-secret-password'], capture_output=True, text=True).stdout
        if ({} == dict_info_kpis):
            for case in dict_info_kpis_and_others['all_test_case']:
                result_to_store_temp = result_to_store
                result_to_store_temp['test_case'] = case[5:]
                result_to_store_temp['kpi_key'] = '-'
                result_to_store_temp['kpi_value'] = '-'
                result_to_store_temp['test_result'] = 'FAILED'
                timestamp = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S") 
                # promotion needed with timestamp
                result_to_store_temp['test_date'] = timestamp
                result_to_store_temp['created'] = timestamp
                result_to_store_temp['modified'] = timestamp
                try:
                    response = requests.post(store_url, data=json.dumps(result_to_store_temp), verify="/home/cert.pem", headers={'Content-Type': 'application/json'}, auth=(portal_username, portal_password))
                    print(response.json())
                    print("Test result uploaded")
                except Exception as e:
                    print("An exception occurs...")
                    print(e)
        else:
            for kpi in dict_info_kpis:
                result_to_store_temp = result_to_store
                result_to_store_temp['test_case'] = kpi
                if ([] == list(dict_info_kpis[kpi]['metrics'].keys())):
                    result_to_store_temp['kpi_key'] = '-'
                    result_to_store_temp['kpi_value'] = '-'
                    result_to_store_temp['test_result'] = 'FAILED'
                else:
                    result_to_store_temp['kpi_key'] = list(dict_info_kpis[kpi]['metrics'].keys())[0]
                    result_to_store_temp['kpi_value'] = dict_info_kpis[kpi]['metrics'][result_to_store_temp['kpi_key']]
                    result_to_store_temp['test_result'] = 'PASS'
                result_to_store_temp['test_time'] = dict_info_kpis[kpi]['test_time']
                # result_to_store_temp['cumulus_uri'] = dict_info_kpis[kpi]['cumulus_url']
                timestamp = datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S") 
                # promotion needed with timestamp
                result_to_store_temp['test_date'] = timestamp
                result_to_store_temp['created'] = timestamp
                result_to_store_temp['modified'] = timestamp
                try:
                    response = requests.post(store_url, data=json.dumps(result_to_store_temp), verify="/home/cert.pem", headers={'Content-Type': 'application/json'}, auth=(portal_username, portal_password))
                    print(response.json())
                except Exception as e:
                    print("An exception occurs...")
                    print(e)

    def get_inner_key_from_dict(self, outterDict, outterDictKey):
        innerDict = outterDict[outterDictKey]
        innerDictKeyList = list(innerDict.keys())
        if (len(innerDictKeyList) > 1):
            return innerDict, innerDictKeyList
        return innerDict, innerDictKeyList[0]