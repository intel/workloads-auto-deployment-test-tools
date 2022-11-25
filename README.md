# WSF-VaaS

## Introduction

This tool provides the ability to configure and run WSF workload automatically, the configuration contains: Kubernetes installation, Kernel update, Kernel arguments update.
### 
It contains two parts:
1. The frontend page which use VueJS+Django to develop, user can manage servers, and choose workload to configure and run
2. The backend service use python ang go to develop, it does the tasks which sent by frontend page and finally call jenkins pipeline to complete the workload running.
###
![architectrue.png](architectrue.png)

## License

See [LICENSE](LICENSE) for details.


## Related projects documentation
Refer to the directory "doc"

## Release note
What is new in this release:
- Web UI for user easier to do provision and validation, server management, orchestration
- Auto provision ability for: Kubernetes, Kernel update, Kernel arguments update
- Validation ability to run workload benchmark based on Workload service framework 

Release Impact 
- In network that could not access to internet need extra offline installation effort to initial this tool  

Known issue
- KVM installation function is not fully ready
- K8s installation may fail on some un-clean CentOS environment