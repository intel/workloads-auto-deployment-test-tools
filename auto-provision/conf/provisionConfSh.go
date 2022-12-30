package conf

const TemplateSh = `#!/usr/bin/env bash
deployDir="/auto_provision_services"
jobId={{.JobId}}
frontApi="http://10.67.119.211:8899/local/api/job/{{.JobId}}/"
# host machines to be deployed
deployHost=(
		"name,ansible_host,ip,username,hostname,password"
		{{- range $_, $host := .DeployHost}}
        "{{$host.Name}},{{$host.AnsibleHost}},{{$host.Ip}},{{$host.Username}},{{$host.Hostname}},{{$host.Password}}"
		{{- end}}
)

# kubernetes
kubernetes_deploy="{{.KubernetesDeploy}}"
kubernetesInstallMethod="{{.KubernetesInstallMethod}}" # host vm docker
declare -A kubernetesArgs
kubernetesArgs=(
        ["kube_version"]="{{.KubernetesArgs.KubeVersion}}"  #v1.23.5
        ["kube_network_plugin"]="{{.KubernetesArgs.KubeNetworkPlugin}}" # cilium, calico, weave or flannel
        ["container_manager"]="{{.KubernetesArgs.ContainerManager}}" #  docker, crio, containerd
        ["dashboard_enabled"]="{{.KubernetesArgs.DashboardEnabled}}" #  true false
        ["helm_enabled"]="{{.KubernetesArgs.HelmEnabled}}" # true false
        ["registry_enabled"]="{{.KubernetesArgs.RegistryEnabled}}" # true false
        ["ingress_nginx_enabled"]="{{.KubernetesArgs.IngressNginxEnabled}}" # true false
        ["ingress_nginx_host_network"]="{{.KubernetesArgs.IngressNginxHostNetwork}}" # true false
        ["krew_enabled"]="{{.KubernetesArgs.KrewEnabled}}"
)

# workload args
jenkins="{{.Jenkins}}"
workloadName="{{.WorkloadName}}"
jsfRepo="{{.JsfRepo}}"
commit="{{.Commit}}"
filterCase="{{.FilterCase}}"
workloadParameter="{{.WorkloadParameter}}"
registry="{{.Registry}}"
platforms="{{.Platforms}}"

# software
softwarepackage="{{.SoftwarePackage}}"
softwarepackageArgs=(
        "name,scriptArgs"
		{{- range $_, $args := .SoftwarePackageArgs}}
        "{{$args.Name}}","{{$args.ScriptArgs}}"
		{{- end}}
)

# system
system_deploy="{{.SystemDeploy}}"
os_update="{{.OsUpdate}}"
os="{{.Os}}"                      # ""use system default values        example: ubuntu20.04 / centos8
Kernel_update="{{.KernelUpdate}}"
kernelVersion="{{.KernelVersion}}"           # ""use system default values        example: 5.8
kernelArgs_update="{{.KernelArgsUpdate}}"
kernelArgs='{{.KernelArgs}}'
# bios args
bios_update="{{.BiosUpdate}}"
biosArgs='BIOS_CONFIG: [
{{- $le:= len .BiosArgs}}
{{- $le:= sub $le 1}}
{{- range $index, $args := .BiosArgs}}
  {{- if eq $le $index}}
  {"knob":"{{$args.Knob}}" , "prompt": "{{$args.Prompt}}", "value": "{{$args.Value}}"}
  {{- else}}
  {"knob":"{{$args.Knob}}" , "prompt": "{{$args.Prompt}}", "value": "{{$args.Value}}"},
  {{- end}}
{{- end}}
]'

# virtual machine
vm_deploy="{{.VmDeploy}}"
vm_docker="{{.VmDocker}}"
declare -A vmosArgs
vmosArgs=(
        ["osNumber"]="{{.VmosArgs.OsNumber}}"
        ["osType"]="{{.VmosArgs.OsType}}"
        ["vmName"]="{{.VmosArgs.VmName}}"
        ["memory"]="{{.VmosArgs.Memory}}"
        ["cpuNumber"]="{{.VmosArgs.CpuNumber}}"
        ["disk"]="{{.VmosArgs.Disk}}"
)

# email
sender="{{.Sender}}"
receivers="{{.Receivers}}" #example receivers="renlex.fu@intel.com,owen.zhang@intel.com"
`
