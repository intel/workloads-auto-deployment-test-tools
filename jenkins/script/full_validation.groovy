/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/

def build_time = new Date()
build_time = build_time.format("MM-dd-yyyy", TimeZone.getTimeZone('UTC'))
def sf_revision
def test_session
def wl_list
@NonCPS
def getSorted(def mapSizeMap){
    mapSizeMap.sort(){ a, b -> a.key <=> b.key }
}

pipeline {
    options {
        buildDiscarder(logRotator(daysToKeepStr: '60', numToKeepStr: '2000'))
    }
    agent {
        label 'node1'
    }
  parameters {
    string(name: 'front_job_id', defaultValue: '', description: 'Related job in frontend.')
    string(name: 'platforms', defaultValue: 'ICX', description: 'Run validation on specific platforms, separate with comma, e.g: SPR,ICX, default as null will run tests on all supported platforms.')
    string(name: 'sf_commit', defaultValue: 'main', description: '')
    string(name: 'repo', defaultValue: 'https://github.com/intel-innersource/applications.benchmarking.benchmark.external-platform-hero-features.git', description: 'github repo address')
    string(name: 'registry', defaultValue: '192.168.0.160:5000', description: 'docker registry')
    string(name: 'instance_api', defaultValue: 'https://127.0.0.1:8899/local/api/job/', description: 'frontend api')
    string(name: 'artifactory_url', defaultValue: 'http://127.0.0.1:8082/artifactory', description: 'artifactory url')
    string(name: 'django_execution_result_url', defaultValue: 'https://127.0.0.1:8899/local/api/test_result/', description: 'store execution results')
    string(name: 'session', defaultValue: '', description: 'used for separate testing.')
    string(name: 'workload_list', defaultValue: '', description: 'separated with ";",e.g: BoringSSL;Bert-Large. Or Encode-3dnr;Nginx  This parameter must match with "customer"')
    choice(name: 'customer', choices: ['main', 'tencent', 'ali'], description: 'main stands for mainline workloads direct under workload folder not customer workloads')
    booleanParam(name: 'emon', defaultValue: '', description: '')
    booleanParam(name: 'baremetal', defaultValue: true, description: '')
    booleanParam(name: 'vm', defaultValue: '', description: '')
    booleanParam(name: 'tdx', defaultValue: '', description: '')
    booleanParam(name: 'snc4', defaultValue: '', description: '')
    string(name: 'filter_case', defaultValue: '', description: 'Regex string for ctest, if set, only run the cases which match this string. If start with !, then these cases will not run.')
    string(name: 'exclude_case', defaultValue: '', description: 'if set, exclude the cases which match this string. These cases will not run..')
    string(name: 'cumulus_tags', defaultValue: '', description: 'use to tag cumulus run especially for release run. different tags are separated with comma. e.g: tag1,tag2')
    booleanParam(name: 'run_on_previous_hw', defaultValue: true, description: 'Run validation on the same HW configuration with previous.')
    string(name: 'cluster_file', defaultValue: 'cluster.yaml', description: 'To use different cluster.yaml file in artifactory')
    string(name: 'limited_node_number', defaultValue: '4', description: 'Limit some cases execute if their required nodes are greater than the specified value, and mark them as no_run.')
    string(name: 'workload_params', defaultValue: '', description: 'workload exposed params key-value pair. e.g: param1=value1 param2=value2')
    string(name: 'workload_test_config_yaml', defaultValue: '', description: 'low end or high end configuration file from workload folder, will ignore workload_params', trim: true)
    string(name: 'controller_ip', defaultValue: '', description: 'controller ip')
    string(name: 'worker_ip_list', defaultValue: '', description: 'worker ips, join with \',\' ')
    booleanParam(name: 'k8s_reset', defaultValue: false, description: 'Reset k8s cluster, be cautious to enable it as it will only setup k8s with selected nodes.')
    string(name: 'ctest_option', defaultValue: '', description: 'ctest.sh options like --loop to run the ctest commands sequentially.', trim: true)
  }
    stages {
        stage('download one source repo'){
            steps {
                script {
                    // println env.BUILD_URL
                    if (env.session != ''){
                        sf_revision = env.session.split('_')[-1]
                    }
                    else{
                        sf_revision = env.sf_commit
                    }

                    sh "rm -rf validation && git clone ${env.repo} validation && cd validation && git checkout ${sf_revision}"

                    commitId = sh(returnStdout: true, script: 'cd validation && git rev-parse HEAD')
                    commitId = commitId?.substring(0,8)
                    wiki_commitId = "auto-provision"

                    if (env.workload_list && env.customer == 'ali') {
                        wl_list = 'customer/ali/' + env.workload_list
                        wl_list = wl_list.replaceAll(";", ";customer/ali/")
                    }
                    else if (env.workload_list && env.customer == 'tencent') {
                        wl_list = 'customer/tencent/' + env.workload_list
                        wl_list = wl_list.replaceAll(";", ";customer/tencent/")
                    }else if (env.customer == 'ali' || env.customer == 'tencent') {
                        wl_list = 'customer/' + env.customer + '/'
                    } else {
                        wl_list = env.workload_list
                    }

                    build job:"image" , parameters:[
                        [$class: "StringParameterValue", name: "front_job_id", value: "${env.front_job_id}"],
                        [$class: "StringParameterValue", name: "commit", value: "${env.sf_commit}"],
                        [$class: "StringParameterValue", name: "registry", value: "${env.registry}"],
                        [$class: "StringParameterValue", name: "platform", value: "${env.platforms}"],
                        [$class: "StringParameterValue", name: "workload_list", value: "${wl_list}"],
                        [$class: "StringParameterValue", name: "repo", value: "${env.repo}"]
                        ]

                    currentBuild.displayName = "${env.customer}_${build_time}_${BUILD_ID}_${wiki_commitId}_${commitId}"
                    if (env.session != '') {
                        test_session = env.session
                    }
                    else {
                        if (env.cumulus_tags != '') {
                            test_session = "${env.customer}_release_${build_time}_${BUILD_ID}_${wiki_commitId}_${commitId}"
                        }
                        else {
                            test_session = "${env.customer}_${build_time}_${BUILD_ID}_${wiki_commitId}_${commitId}"
                        }
                    }
                }
            }
        }
        stage('run all workloads') {
            steps {
                script {
                    def platforms
                    if (env.platforms != ''){
                        platforms = env.platforms
                        platforms = platforms.split(",");
                    }
                    else {
                        platforms = sh (
                        script: 'cd validation && cat workload/platforms',
                        returnStdout: true
                        )
                        platforms = platforms.split("\n");
                    }

                    def files
                    if (env.workload_list && env.customer != 'main') {
                        files = wl_list.split(';')
                    } else if (env.workload_list && env.customer == 'main') {
                        files = env.workload_list.split(';')
                    } else if (env.customer != 'main' && !env.workload_list) {
                        files = sh (
                        script: "cd validation/workload/customer && find ${env.customer} -mindepth 2 -maxdepth 2 -name validate.sh",
                        returnStdout: true
                        )
                        files = files.replaceAll('/validate.sh','').split("\n")
                        files = files.collect {"customer/" + it}
                    }
                    else {
                        files = sh (
                        script: 'cd validation && find workload -mindepth 2 -maxdepth 2 -name validate.sh',
                        returnStdout: true
                        )
                        files = files.replaceAll('/validate.sh','')
                        files = files.replaceAll('workload/','').split("\n");
                    }

                    def workloads = [:]
                    for (p in platforms) {
                        for (f in files) {
                            def fvar
                            fvar = "${f}".split("/")[-1]
                            def pvar = "${p}"
							workloads["${pvar}/${fvar}"] = {
								stage("${pvar}/${fvar}") {
									script {
										build job:"benchmark" , parameters:[
                                            [$class: "StringParameterValue", name: "front_job_id", value: "${env.front_job_id}"],
											[$class: "StringParameterValue", name: "platform", value: "${pvar}"],
											[$class: "StringParameterValue", name: "repo", value: "${env.repo}"],
											[$class: "StringParameterValue", name: "registry", value: "${env.registry}"],
											[$class: "StringParameterValue", name: "instance_api", value: "${env.instance_api}"],
											[$class: "StringParameterValue", name: "artifactory_url", value: "${env.artifactory_url}"],
                                            [$class: "StringParameterValue", name: "django_execution_result_url", value: "${env.django_execution_result_url}"],
											[$class: "StringParameterValue", name: "commit_id", value: "${env.sf_commit}"],
											[$class: "BooleanParameterValue", name: "emon", value: "${emon}"],
											[$class: "BooleanParameterValue", name: "vm", value: "${vm}"],
											[$class: "BooleanParameterValue", name: "baremetal", value: "${baremetal}"],
											[$class: "BooleanParameterValue", name: "snc4", value: "${snc4}"],
											[$class: "BooleanParameterValue", name: "tdx", value: "${tdx}"],
											[$class: "StringParameterValue", name: "workload", value: "${fvar}"],
											[$class: "StringParameterValue", name: "session", value: "${test_session}"],
											[$class: "BooleanParameterValue", name: "run_on_previous_hw", value: "${run_on_previous_hw}"],
											[$class: "StringParameterValue", name: "cumulus_tags", value: "${cumulus_tags}"],
											[$class: "StringParameterValue", name: "filter_case", value: "${filter_case}"],
											[$class: "StringParameterValue", name: "exclude_case", value: "${exclude_case}"],
											[$class: "StringParameterValue", name: "customer", value: "${env.customer}"],
											[$class: 'StringParameterValue', name: 'limited_node_number', value: "${limited_node_number}"],
											[$class: 'StringParameterValue', name: 'cluster_file', value: "${cluster_file}"],
											[$class: 'StringParameterValue', name: 'workload_params', value: "${workload_params}"],
											[$class: 'StringParameterValue', name: 'workload_test_config_yaml', value: "${workload_test_config_yaml}"],
											[$class: 'StringParameterValue', name: 'controller_ip', value: "${controller_ip}"],
											[$class: 'StringParameterValue', name: 'worker_ip_list', value: "${worker_ip_list}"],
                                            [$class: 'BooleanParameterValue', name: 'k8s_reset', value: "${k8s_reset}"],
											[$class: "StringParameterValue", name: "ctest_option", value: "${ctest_option}"],
										]

									}
								}
							}
                        }
                    }
                    def sorted_workloads = getSorted(workloads)
                    parallel sorted_workloads
                }
            }
        }
    }
    post {
        always {
            script{
                cleanWs()
                println "ok"
            }
        }
    }
}

