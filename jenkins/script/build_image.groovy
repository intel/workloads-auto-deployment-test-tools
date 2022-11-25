def build_time = new Date()
build_time = build_time.format("MM-dd-yyyy", TimeZone.getTimeZone('UTC'))
def commitId

pipeline {
	agent {
		label 'node1'
	}
	parameters {
		string(name: 'commit', defaultValue: 'main', description: '')
		string(name: 'registry', defaultValue: '10.166.44.56:5000', description: '')
		string(name: 'platform', defaultValue: 'ICX', description: '')
		string(name: 'workload_list', defaultValue: '', description: 'To build workload list, default "" , means all workload. Separated with ";",e.g: BoringSSL;Bert-Large;CNN;customer/ali/redis')
		string(name: 'repo', defaultValue: 'https://github.com/intel-innersource/applications.benchmarking.benchmark.external-platform-hero-features.git', description: 'WSF repo')
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
    					script: "cd validation &&  rm -rf build && mkdir build && cd build && echo accept | cmake -DPLATFORM=${platform} -DREGISTRY=${registry} -DBACKEND=cumulus -DRELEASE=${commitId} -DACCEPT_LICENSE=ALL ../",
    					returnStdout: true
    					)
			    	if (env.workload_list != '') {
    				    workload_list = env.workload_list
    				    workload_list = workload_list.split(";")
						for (workload in workload_list) {
    					        println ("=================================Build workload: ${workload} image========================================")
    					        sh (returnStdout: true, script: "cd validation/build/workload/${workload} && make")
    					        if (env.registry.startsWith("amr-registry-pre.caas.intel.com")) {
                                    docker_image_list = sh (returnStdout: true, script: "docker images|grep caas |grep -v cumulus |grep ${commitId} |cut -d ' ' -f 1")
                                    docker_image_list = docker_image_list.split("\n")
                                    for (images_and_tag in docker_image_list) {
                                        image = images_and_tag.split('/')[-1]
                                        image_name = "${registry}/${image}:${commitId}"
                                        tar_name = "${image}-${commitId}.tar"
                                        image_num = sh (returnStdout: true, script: "aws s3 ls s3://cumulus/sf-cwr-test/ | grep ${tar_name} | wc -l")
                                        image_num = image_num.replaceAll("\r|\n", "")
                                        if ("${image_num}" == '0') {
                                            sh "docker save --output ./${tar_name} ${image_name} && aws s3 cp ./${tar_name} s3://cumulus/sf-cwr-test/"
                                        }
                                        else {
                                            println ("${tar_name} already in S3 ...")
                                        }
                                    }
                                }
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

