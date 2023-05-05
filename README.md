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
- Added grafana dashboard to show execution status
- Released upgrade documentation
- Supports WSF new released workloads 

Release Impact 
- In network that could not access to internet need extra offline installation effort to initial this tool  

Upcoming Release
- Support staging folder to allow user to run customized workloads
