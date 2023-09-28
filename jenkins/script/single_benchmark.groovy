/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/

def build_time = new Date()
build_time = build_time.format('MM-dd-yyyy', TimeZone.getTimeZone('UTC'))
def revision
def target

pipeline {
    options {
        buildDiscarder(logRotator(daysToKeepStr: '60', numToKeepStr: '2000'))
    }
    agent {
        label 'node1'
    }
    parameters {
        string(name: 'front_job_id', defaultValue: '', description: 'Related Job in frontend.')
        string(name: 'workload', defaultValue: 'Kafka', description: '')
        string(name: 'platform', defaultValue: 'ICX', description: '')
        string(name: 'session', defaultValue: '', description: 'session id for full validation, combination with "date"_"full validation job id"_"wiki commit"_"cumulus commit"_"repo commit", for manual run, use "repo commit" is enough')
        string(name: 'repo', defaultValue: 'https://github.com/intel-innersource/applications.benchmarking.benchmark.external-platform-hero-features.git', description: 'github repo address')
        string(name: 'registry', defaultValue: '127.0.0.1:5000', description: 'docker registry')
        string(name: 'instance_api', defaultValue: 'https://127.0.0.1:8899/local/api/instance/', description: 'get instance list api')
        string(name: 'artifactory_url', defaultValue: 'http://127.0.0.1:8082/artifactory', description: 'artifactory url')
        string(name: 'django_execution_result_url', defaultValue: 'https://127.0.0.1:8899/local/api/test_result/', description: 'store execution results')
        string(name: 'commit_id', defaultValue: 'main', description: 'commit id of the provided repo, also could be branch name')
        booleanParam(name: 'emon', defaultValue: '', description: '')
        string(name: 'timeout', defaultValue: '60000,3600', description: 'timeout for execution, first one is for pod execution timeout, second one is for pod ready timeout.')
        booleanParam(name: 'vm', defaultValue: '', description: '')
        booleanParam(name: 'baremetal', defaultValue: true, description: '')
        booleanParam(name: 'tdx', defaultValue: '', description: 'Currently only for SPR platform')
        booleanParam(name: 'snc4', defaultValue: '', description: 'Currently only for SPR platform')
        string(name: 'cumulus_tags', defaultValue: '', description: 'use to tag cumulus run especially for release run. different tags are separated with comma. e.g: tag1,tag2')
        string(name: 'run_on_specific_hw', defaultValue: '', description: 'hw config id from cluster.yaml, if defined, all test case will run on this config.')
        booleanParam(name: 'run_on_previous_hw', defaultValue: true, description: 'Run on the same HW configuration with previous.')
        string(name: 'filter_case', defaultValue: '', description: 'Regex string for ctest, if set, only run the cases which match this string. If start with !, then these cases will not run.')
        string(name: 'exclude_case', defaultValue: '', description: 'if set, exclude the cases which match this string. These cases will not run..')
        string(name: 'pull_request_id', defaultValue: '', description: 'used for gated test')
        string(name: 'workload_params', defaultValue: '', description: 'workload exposed params key-value pair. e.g: param1=value1 param2=value2')
        string(name: 'workload_test_config_yaml', defaultValue: '', description: 'low end or high end configuration file from workload folder, will ignore workload_params', trim: true)
        choice(name: 'customer', choices: ['main', 'tencent', 'ali'], description: 'main stands for mainline workloads direct under workload folder not customer workloads')
        string(name: 'cluster_file', defaultValue: 'cluster.yaml', description: 'To use different cluster.yaml file in artifactory')
        string(name: 'limited_node_number', defaultValue: '4', description: 'Limit some cases execute if their required nodes are greater than the specified value, and mark them as no_run.')
        string(name: 'parallel_run_case_number', defaultValue: '1', description: 'Specifies the number of cases to run in parallel during the workload validation.')
        string(name: 'controller_ip', defaultValue: '', description: 'controller ip')
        string(name: 'worker_ip_list', defaultValue: '', description: 'worker ips, join with \',\' ')
        booleanParam(name: 'k8s_reset', defaultValue: false, description: 'Reset k8s cluster, be cautious to enable it as it will only setup k8s with selected nodes.')
        string(name: 'ctest_option', defaultValue: '', description: 'ctest.sh options like --loop to run the ctest commands sequentially.', trim: true)
    }
    environment {
        JENKINS_SCRIPT_REPO = 'https://github.com/intel-sandbox/WSF-VaaS.git'
    }
    stages {
        stage('Check WorkSpace clean'){
            steps {
                script{
                    out_code=sh(script:"ls ${workspace}/validation",returnStatus:true)
                    if(out_code == 0){
                        println "**************************************"
                        println "|       WorkSpace not clean ...      |"
                        println "**************************************"
                        sh "rm -rf ${workspace}/run_uri"
                        sh "rm -rf ${workspace}/*.json"
                        sh "rm -rf ${workspace}/logs"
                        sh "rm -rf ${workspace}/result"
                        sh "rm -rf ${workspace}/pool"
                        sh "rm -rf ${workspace}/dist"
                    }
                }
            }
        }

        stage('Prepare') {
            steps {
                script {
                    sh "mkdir -p pool"
                    // Download wsf repo
                    sh "rm -rf validation && git clone ${env.repo} validation && cd validation && git checkout ${env.commit_id}"
                    // Copy jenkins script
                    sh "mkdir -p $WORKSPACE/script/jenkins"
                    sh "cp -r /var/lib/script/ $WORKSPACE/script/jenkins"
                    // sh "rm -rf script && git clone ${JENKINS_SCRIPT_REPO} script && cd script && git checkout external_release"
                    if (env.session != null && !env.session.isEmpty()) {
                        env.build_session = env.session
                        revision = session.split('_')[-1]
                        display_name = "${session}_${platform}_${workload}_${BUILD_ID}"
                    }
                    else
                    {
                        revision = 'master'
                        display_name = "manual_${build_time}_${platform}_${workload}_${BUILD_ID}"
                        env.build_session = "manual_${build_time}_${BUILD_ID}_master"
                    }
                    if (env.vm == true) {
                        currentBuild.displayName = "${display_name}_VM"
                        env.platform_name = "${platform}-VM"Q
                    }
                    else
                    {
                        currentBuild.displayName = "${display_name}"
                        env.platform_name = platform
                    }
                    // sh "rm -rf validation && git clone ${env.repo} validation && cd validation && git checkout ${env.commit_id}"
                    sh "python3 script/jenkins/script/cluster_generate.py ${controller_ip} ${worker_ip_list} ${platform} ${instance_api} ${registry}"
                }
            }
        }
        stage('Run workload benchmark') {
            steps {
                script {
                    //sh "${workspace}/script/jenkins/script/benchmark $build_session benchmark || echo \$? > status"
                    benchmark_status=sh(script:"${workspace}/script/jenkins/script/benchmark $build_session benchmark", returnStatus:true)
                    sh(script:"echo ${benchmark_status} > status")
                }
            }
        }
    }
    post {
        always {
            script {
                // println env.BUILD_URL
                def benchmark_status = readFile(file: 'status').trim()
                println "benchmark_status: $benchmark_status"
                if (benchmark_status != "0") {
                    echo "Fatal error: benchmark failed."
                    currentBuild.result = 'FAILURE'
                }
                println "Create and publish artifacts."
                benchmark_result = sh (script:". /etc/profile > /dev/null 2>&1 && ${workspace}/script/jenkins/script/benchmark $build_session artifacts", returnStatus:true)
                def art_url="${artifactory_url}"
                out = sh (script:"ls ${workspace}/validation/build/workload/${workload}/Testing/Temporary", returnStatus:true)
                if (out == 0) {
                    def server = Artifactory.newServer url: art_url, credentialsId: 'jfrog'
                        def uploadSpec = """{
                        "files": [
                        {
                        "pattern": "logs/",
                        "target": "auto_provision/${build_session}/${platform_name}_${workload}_${BUILD_ID}/",
                        "props": "retention.days=365",
                        "recursive": "true",
                        "flat": "false"
                        },
                        {
                        "pattern": "*${workload}.json",
                        "target": "auto_provision/${build_session}/execution/${platform_name}_${workload}_${BUILD_ID}.json",
                        "props": "retention.days=365",
                        "recursive": "true",
                        "flat": "false"
                        }
                        ]
                        }"""
                        server.bypassProxy = true
                        server.upload spec: uploadSpec
                }
                script {
                    if(fileExists("${workspace}/run_uri")){
                        runs = sh (script:"cat ${workspace}/run_uri", returnStdout:true)
                        runs = runs.split('\n')
                        for (run in runs) {
                            sh "docker kill ${run} || echo 0"
                        }
                    }
                }
                cleanWs()
                if (benchmark_result != 0) {
                    echo "Fatal error: result failed."
                    currentBuild.result = 'FAILURE'
                }
            }
        }
    }
}

