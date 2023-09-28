# README

## Introduction

This is the README for TWDT, a web application used to manage Jenkins tasks and WSF test K8s clusters. With the help of WSF, we can easily create Jenkins tasks and specify on which clusters the WSF Workload tasks runs on this TWDT application.

### 
It contains two parts:
1. A front-end web application developed by VueJS + Django, users can manage server instances, configure workloads and trigger Jenkins tasks with a few simple clicks.
2. A backend service developed by Python ang Go, it receives messages from front-end pages and call jenkins pipeline to build WSF images and schedule test cases on demmanded clusters.
###
![architectrue.png](architectrue.png)

## License

See [LICENSE](LICENSE) for details.


## Related projects documentation
Refer to the directory "doc"

## Release note
What is new in this release:
- Enhanced UI exeprience, workload execution become simpler
- Enhanced installation experience, added a setup scripts to simplify the installation

Release Impact 
- In network that could not access to internet need extra offline installation effort to initial this tool  

Upcoming Release
- KVM provisioning support

## Expected operating sysstem
This application works well with Ubuntu server 22.04 LTS.

