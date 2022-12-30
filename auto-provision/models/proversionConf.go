package models

type DeployHost struct {
	Name        string `json:"name"`
	AnsibleHost string `json:"ansible_host"`
	Ip          string `json:"ip"`
	Username    string `json:"username"`
	Hostname    string `json:"hostname"`
	Password    string `json:"password"`
}

type KubernetesArgs struct {
	KubeVersion             string `json:"kube_version"`
	KubeNetworkPlugin       string `json:"kube_network_plugin"`
	ContainerManager        string `json:"container_manager"`
	DashboardEnabled        string `json:"dashboard_enabled"`
	HelmEnabled             string `json:"helm_enabled"`
	RegistryEnabled         string `json:"registry_enabled"`
	IngressNginxEnabled     string `json:"ingress_nginx_enabled"`
	IngressNginxHostNetwork string `json:"ingress_nginx_host_network"`
	KrewEnabled             string `json:"krew_enabled"`
}

type SoftwarePackageArgs struct {
	Name       string `json:"name"`
	ScriptArgs string `json:"scriptArgs"`
}

type VmosArgs struct {
	OsNumber  string `json:"osNumber"`
	OsType    string `json:"osType"`
	VmName    string `json:"vmName"`
	Memory    string `json:"memory"`
	CpuNumber string `json:"cpuNumber"`
	Disk      string `json:"disk"`
}

type BiosArgs struct {
	Knob   string `json:"knob" binding:"-"`
	Prompt string `json:"prompt" binding:"-"`
	Value  string `json:"value"  binding:"-"`
}

type ProversionConf struct {
	JobId                   string                `json:"jobId"`
	DeployHost              []DeployHost          `json:"deployHost"`
	KubernetesDeploy        string                `json:"kubernetes_deploy"`
	KubernetesInstallMethod string                `json:"kubernetesInstallMethod"`
	KubernetesArgs          KubernetesArgs        `json:"kubernetesArgs"`
	Jenkins                 string                `json:"jenkins"`
	WorkloadName            string                `json:"workloadName"`
	JsfRepo                 string                `json:"jsf_repo"`
	Commit                  string                `json:"commit"`
	FilterCase              string                `json:"filter_case"`
	WorkloadParameter       string                `json:"workload_parameter"`
	Registry                string                `json:"registry"`
	Platforms               string                `json:"platforms"`
	SoftwarePackage         string                `json:"softwarepackage"`
	SoftwarePackageArgs     []SoftwarePackageArgs `json:"softwarepackageArgs"`
	SystemDeploy            string                `json:"system_deploy"`
	OsUpdate                string                `json:"os_update" binding:"-"`
	Os                      string                `json:"os" binding:"-"`
	KernelUpdate            string                `json:"Kernel_update"`
	KernelVersion           string                `json:"kernelVersion"`
	KernelArgsUpdate        string                `json:"kernelArgs_update"`
	KernelArgs              string                `json:"kernelArgs"`
	BiosUpdate              string                `json:"bios_update" binding:"-"`
	BiosArgs                []BiosArgs            `json:"biosArgs" binding:"-"`
	VmDeploy                string                `json:"vm_deploy"`
	VmDocker                string                `json:"vm_docker"`
	VmosArgs                VmosArgs              `json:"vmosArgs"`
	Sender                  string                `json:"sender"`
	Receivers               string                `json:"receivers"`
}
