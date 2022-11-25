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
    string(name: 'platforms', defaultValue: 'ICX', description: 'Run validation on specific platforms, separate with comma, e.g: SPR,ICX, default as null will run tests on all supported platforms.')
    string(name: 'sf_commit', defaultValue: 'main', description: '')
    string(name: 'repo', defaultValue: 'https://github.com/intel-innersource/applications.benchmarking.benchmark.external-platform-hero-features.git', description: 'github repo address')
    string(name: 'registry', defaultValue: '192.168.0.160:5000', description: 'docker registry')
    string(name: 'instance_api', defaultValue: 'https://127.0.0.1:8899/local/api/job/', description: 'frontend api')
    string(name: 'artifactory_url', defaultValue: 'http://127.0.0.1:8082/artifactory', description: 'artifactory url')
    string(name: 'session', defaultValue: '', description: 'used for separate testing.')
    string(name: 'workload_list', defaultValue: '', description: 'separated with ";",e.g: BoringSSL;Bert-Large. Or Encode-3dnr;Nginx  This parameter must match with "customer"')
    choice(name: 'customer', choices: ['main', 'tencent', 'ali'], description: 'main stands for mainline workloads direct under workload folder not customer workloads')
    booleanParam(name: 'emon', defaultValue: '', description: '')
    booleanParam(name: 'baremetal', defaultValue: true, description: '')
    booleanParam(name: 'vm', defaultValue: '', description: '')
    booleanParam(name: 'tdx', defaultValue: '', description: '')
    booleanParam(name: 'snc4', defaultValue: '', description: '')
    string(name: 'filter_case', defaultValue: '', description: 'Regex string for ctest, if set, only run the cases which match this string. If start with !, then these cases will not run.')
    string(name: 'cumulus_tags', defaultValue: '', description: 'use to tag cumulus run especially for release run. different tags are separated with comma. e.g: tag1,tag2')
    booleanParam(name: 'run_on_previous_hw', defaultValue: true, description: 'Run validation on the same HW configuration with previous.')
    string(name: 'cluster_file', defaultValue: 'cluster.yaml', description: 'To use different cluster.yaml file in artifactory')
    string(name: 'limited_node_number', defaultValue: '4', description: 'Limit some cases execute if their required nodes are greater than the specified value, and mark them as no_run.')
    string(name: 'controller_ip', defaultValue: '', description: 'controller ip')
    string(name: 'worker_ip_list', defaultValue: '', description: 'worker ips, join with \',\' ')
  }
    stages {
        stage('download one source repo'){
            steps {
                script {
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
                    workload_map = [:]
                    for (file in files) {
                        workload = "${file}".split("/")[-1]
                        workload_name = sh (
                        script: "cat validation/workload/${file}/CMakeLists.txt |grep 'add_workload('",
                        returnStdout: true
                        )
                        workload_name = workload_name.split('"')[1]
                        workload_map[workload] = workload_name
                    }

                    def workloads = [:]
                    for (p in platforms) {
                        def supported_platform = [:]
                        sh "cd validation && rm -rf build && mkdir build && cd build && cmake -DPLATFORM=${p} -DREGISTRY=0.0.0.0:5000 -DBACKEND=cumulus ../"
                        supported_platform = sh (
                        script: 'cd validation/build && make help|grep bom_',
                        returnStdout: true
                        )

                        for (f in files) {
                            def fvar
                            fvar = "${f}".split("/")[-1]
                            def pvar = "${p}"
                            if(supported_platform.contains(workload_map[fvar].toLowerCase())) {
                                workloads["${pvar}/${fvar}"] = {
                                    stage("${pvar}/${fvar}") {
                                        script {
                                            build job:"benchmark" , parameters:[
                                                [$class: "StringParameterValue", name: "platform", value: "${pvar}"],
                                                [$class: "StringParameterValue", name: "repo", value: "${env.repo}"],
                                                [$class: "StringParameterValue", name: "registry", value: "${env.registry}"],
                                                [$class: "StringParameterValue", name: "instance_api", value: "${env.instance_api}"],
                                                [$class: "StringParameterValue", name: "artifactory_url", value: "${env.artifactory_url}"],
                                                [$class: "StringParameterValue", name: "commit_id", value: "${env.sf_commit}"],
                                                [$class: "BooleanParameterValue", name: "emon", value: "${emon}"],
                                                [$class: "BooleanParameterValue", name: "vm", value: "${vm}"],
                                                [$class: "BooleanParameterValue", name: "baremetal", value: "${baremetal}"],
                                                [$class: "BooleanParameterValue", name: "snc4", value: "${snc4}"],
                                                [$class: "BooleanParameterValue", name: "tdx", value: "${tdx}"],
                                                [$class: "StringParameterValue", name: "workload", value: "${fvar}"],
                                                [$class: "StringParameterValue", name: "session", value: "${test_session}"],
                                                [$class: "StringParameterValue", name: "run_on_previous_hw", value: "${run_on_previous_hw}"],
                                                [$class: "StringParameterValue", name: "cumulus_tags", value: "${cumulus_tags}"],
                                                [$class: "StringParameterValue", name: "filter_case", value: "${filter_case}"],
                                                [$class: "StringParameterValue", name: "customer", value: "${env.customer}"],
                                                [$class: 'StringParameterValue', name: 'limited_node_number', value: "${limited_node_number}"],
                                                [$class: 'StringParameterValue', name: 'cluster_file', value: "${cluster_file}"],
                                                [$class: 'StringParameterValue', name: 'controller_ip', value: "${controller_ip}"],
                                                [$class: 'StringParameterValue', name: 'worker_ip_list', value: "${worker_ip_list}"]
                                            ]

                                        }
                                    }
                                }
                            }
                            else
                            {
                                println "${pvar}-${fvar} is not supported"
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

