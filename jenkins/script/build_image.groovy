/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/

def build_time = new Date()
build_time = build_time.format("MM-dd-yyyy", TimeZone.getTimeZone('UTC'))
def commitId

pipeline {
	agent {
		label 'node1'
	}
	parameters {
	    string(name: 'front_job_id', defaultValue: '', description: 'Related Job in frontend.')
		string(name: 'commit', defaultValue: 'main', description: '')
		string(name: 'registry', defaultValue: '10.166.44.56:5000', description: '')
		string(name: 'platform', defaultValue: 'ICX', description: '')
		string(name: 'workload_list', defaultValue: '', description: 'To build workload list, default "" , means all workload. Separated with ";",e.g: BoringSSL;Bert-Large;CNN;customer/ali/redis')
		string(name: 'repo', defaultValue: 'https://github.com/intel-innersource/applications.benchmarking.benchmark.external-platform-hero-features.git', description: 'WSF repo')
		string(name: 'SUT', defaultValue: 'static', description: 'Only support static for now', trim: true)
	}
	environment {
		ONESOURCE_REPO_1 = "github.com/HaitaoLi2Intel/applications.benchmarking.benchmark.platform-hero-features.git"
	}
	stages {
		stage('download one source repo'){
			steps {
				script {
					if (env.commit) {
						revision = "${commit}"
					}
					else
					{
						revision = "master"
					}
					sh "rm -rf validation && git clone ${env.repo} validation && cd validation && git checkout ${revision}"
					commitId = sh(returnStdout: true, script: 'cd validation && git rev-parse HEAD')
					commitId = commitId?.substring(0,8)
					platform = env.platform
					currentBuild.displayName = "${platform}_${build_time}_${BUILD_ID}_${commitId}"
				}
			}
		}
		stage('build all workloads images') {
			steps {
				script {
			    	sh (
    					script: "cd validation &&  rm -rf build && mkdir build && cd build && echo accept | cmake -DPLATFORM=${platform} -DBENCHMARK='' -DREGISTRY=${registry} -DBACKEND=terraform -DRELEASE=${commitId} -DTERRAFORM_SUT=${env.SUT} -DACCEPT_LICENSE=ALL ../",
    					returnStdout: true
    					)
    				sh (script: "cd validation/build && make build_terraform", returnStdout: true)
			    	if (env.workload_list != '') {
    				    workload_list = env.workload_list
    				    workload_list = workload_list.split(";")
						for (workload in workload_list) {
    					        println ("=================================Build workload: ${workload} image========================================")
    					        sh (returnStdout: true, script: "cd validation/build/workload/${workload} && make")
    					    }
					}
					else {
					    println ("=================================Build all workload images========================================")
					    sh (returnStdout: true, script: "cd validation/build && make")
					}
					println ("=================================Building images finished========================================")
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

