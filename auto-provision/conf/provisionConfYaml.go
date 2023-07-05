/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
package conf

const TemplateYaml = `deployDir: /auto_provision_services
jobId: {{.JobId}}
frontApi: "http://10.67.119.211:8899/local/api/job/{{.JobId}}/"
deployHost:
{{- range $_, $host := .DeployHost}}
   - name: {{$host.Name}}
     ansible_host: {{$host.AnsibleHost}}
     ip: {{$host.Ip}}
     username: {{$host.Username}}
     hostname: {{$host.Hostname}}
     password: {{$host.Password}}
{{- end}}
kubernetes_deploy: {{.KubernetesDeploy}}
kubernetesInstallMethod: {{.KubernetesInstallMethod}} 
kubernetesArgs:
  kube_version: {{.KubernetesArgs.KubeVersion}}  
  kube_network_plugin: {{.KubernetesArgs.KubeNetworkPlugin}} 
  container_manager: {{.KubernetesArgs.ContainerManager}} 
  dashboard_enabled: {{.KubernetesArgs.DashboardEnabled}} 
  helm_enabled: {{.KubernetesArgs.HelmEnabled}} 
  registry_enabled: {{.KubernetesArgs.RegistryEnabled}} 
  ingress_nginx_enabled: {{.KubernetesArgs.IngressNginxEnabled}} 
  ingress_nginx_host_network: {{.KubernetesArgs.IngressNginxHostNetwork}} 
  krew_enabled: {{.KubernetesArgs.KrewEnabled}}
jenkins: {{.Jenkins}}
workloadName: {{.WorkloadName}}
jsfRepo: {{.JsfRepo}}
commit: {{.Commit}}
filterCase: "{{.FilterCase}}"
workloadParameter: "{{.WorkloadParameter}}"
registry: {{.Registry}}
platforms: {{.Platforms}}
softwarepackage: "{{.SoftwarePackage}}"
softwarePackageArgs:
{{- range $_, $args := .SoftwarePackageArgs}}
   - name: {{$args.Name}}
     scriptArgs: "{{$args.ScriptArgs}}"
{{- end}}

system_deploy: {{.SystemDeploy}}
os_update: {{.OsUpdate}}
os: {{.Os}}
Kernel_update: {{.KernelUpdate}}
kernelVersion: {{.KernelVersion}}           
kernelArgs_update: {{.KernelArgsUpdate}}
kernelArgs: '{{.KernelArgs}}'
bios_update: {{.BiosUpdate}}
biosArgs:
{{- range $_, $BiosArg := .BiosArgs}}
  - {{$BiosArg}}
{{- end}}
vm_deploy: "{{.VmDeploy}}"
vm_docker: "{{.VmDocker}}"
vmosArgs:
  osNumber: "{{.VmosArgs.OsNumber}}" 
  osType: "{{.VmosArgs.OsType}}" 
  vmName: "{{.VmosArgs.VmName}}" 
  memory: "{{.VmosArgs.Memory}}"
  cpuNumber: {{.VmosArgs.CpuNumber}}
  disk: {{.VmosArgs.Disk}} 
sender: {{.Sender}}
receivers: {{.Receivers}} 
`
