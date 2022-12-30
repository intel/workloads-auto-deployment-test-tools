<template>
<div>
  <TabView>
    <TabPanel header="Provision">
      <template>
        <div class="p-fluid p-formgrid p-grid ml-2 mr-2">
          <div class="p-field p-col-12 p-md-12">
            <el-card class="p-card-background">
              <el-steps :active="active" finish-status="success">
                <el-step title="Workload"></el-step>
                <el-step title="DeployHost Args"></el-step>
                <el-step title="Kubernetes Args"></el-step>
                <el-step title="VM Args"></el-step>
                <el-step title="Workload Args"></el-step>
                <el-step title="Software Args"></el-step>
                <el-step title="System Args"></el-step>
                <el-step title="Email"></el-step>
              </el-steps>
            </el-card>
          </div>
          <div class="p-field p-col-12 p-md-12">
            <el-card class="p-card-background">
              <step-workload :formData="stepFormData" v-if="active===0"></step-workload>
              <step-host :formData="stepFormData" v-if="active===1"></step-host>
              <step-kubernetes :formData="stepFormData" v-if="active===2"></step-kubernetes>
              <step-VMArgs :formData="stepFormData" v-if="active===3"></step-VMArgs>
              <step-workloadArgs :formData="stepFormData" v-if="active===4"></step-workloadArgs>
              <step-softwareArgs :formData="stepFormData" v-if="active===5"></step-softwareArgs>
              <step-systemArgs :formData="stepFormData" v-if="active===6"></step-systemArgs>
              <step-Email :formData="stepFormData" v-if="active===7"></step-Email>
              <div align="right">
              <div v-if="this.active === 7 ? true :false">Complete All Forms</div>
              <el-button style="margin-top: 12px;" @click="prev">Previous</el-button>
              <el-button style="margin-top: 12px;" @click="next">Next</el-button>
              <el-button v-if="this.active === 7 ? true :false" style="margin-top: 12px;" @click="submitProvision">Submit</el-button>
              </div>
            </el-card>
          </div>
        </div>
      </template>
    </TabPanel>
  </TabView>
  <div>
    <Toast position="top-right" />
  </div>
  </div>
</template>

<script>
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import stepFormData from './from'
import StepWorkload from './StepWorkload'
import StepHost from './StepHost'
import StepKubernetes from './StepKubernetes'
import StepWorkloadArgs from './StepWorkloadArgs'
import StepSoftwareArgs from './StepSoftwareArgs'
import StepSystemArgs from './StepSystemArgs'
import StepVMArgs from './StepVMArgs'
import StepEmail from './StepEmail'
import Vue from 'vue'
import TabView from 'primevue/tabview'
import Toast from 'primevue/toast'
import TabPanel from 'primevue/tabpanel'
import axios from 'axios'
import { CSRF_TOKEN } from '../../common/csrf_token'
// import Card from 'primevue/card'
Vue.use(ElementUI)
export default {
  components: {
    StepWorkload,
    StepHost,
    StepKubernetes,
    StepWorkloadArgs,
    StepSystemArgs,
    StepSoftwareArgs,
    StepVMArgs,
    StepEmail,
    TabView,
    TabPanel,
    Toast
  },
  data () {
    return {
      active: 0,
      stepFormData: JSON.parse(JSON.stringify(stepFormData))
    }
  },
  methods: {
    next () {
      if (this.active === 0) {
        if (!this.checkStepWorkload()) return
      }
      if (this.active === 1) {
        if (!this.checkStepHost()) return
      }
      if (this.active === 2) {
        if (!this.checkStepKubernetes()) return
      }
      if (this.active === 3) {
        if (!this.checkStepVMArgs()) return
      }
      if (this.active === 4) {
        if (!this.checkStepWorkloadArgs()) return
      }
      if (this.active === 5) {
        if (!this.checkStepSoftwareArgs()) return
      }
      if (this.active === 6) {
        if (!this.checkStepSystemArgs()) return
      }
      if (this.active++ > 6) this.active = 7
    },
    prev () {
      if (this.active-- < 1) this.active = 0
    },
    checkStepWorkload () {
      if (this.stepFormData.selectedWorkloadName.length !== 0 && this.stepFormData.selectedVersion.length !== 0) {
        return true
      } else {
        this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select BOTH Workload and Version', life: 2000 })
        return false
      }
    },
    checkStepHost () {
      if (this.stepFormData.checkGreen) {
        return true
      } else {
        this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select HOSTS and available time range', life: 2000 })
        return false
      }
    },
    checkStepKubernetes () {
      if (this.stepFormData.deploy_kubernetes) {
        if (this.stepFormData.selectedKubernetesInstallMethod !== null && this.stepFormData.selectedKubernetesInstallMethod.length !== 0 &&
        this.stepFormData.selectedKubernetesVersion !== null && this.stepFormData.selectedKubernetesVersion.length !== 0 &&
        this.stepFormData.selectedKubernetesNetworkPlugin !== null && this.stepFormData.selectedKubernetesNetworkPlugin.length !== 0 &&
        this.stepFormData.selectedContainerManager !== null && this.stepFormData.selectedContainerManager.length !== 0 &&
        this.stepFormData.selectedDashboardEnable !== null && this.stepFormData.selectedDashboardEnable.length !== 0 &&
        this.stepFormData.selectedHEMLEnable !== null && this.stepFormData.selectedHEMLEnable.length !== 0 &&
        this.stepFormData.selectedRegistryEnable !== null && this.stepFormData.selectedRegistryEnable.length !== 0 &&
        this.stepFormData.selectedIngressNginxEnabled !== null && this.stepFormData.selectedIngressNginxEnabled.length !== 0 &&
        this.stepFormData.selectedIngressNginxHostNetwork !== null && this.stepFormData.selectedIngressNginxHostNetwork.length !== 0 &&
        this.stepFormData.selectedKrewEnabled !== null && this.stepFormData.selectedKrewEnabled.length !== 0) {
          return true
        } else {
          this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select a value for Kubernetes items', life: 2000 })
          return false
        }
      } else {
        return true
      }
    },
    checkStepVMArgs () {
      if (this.stepFormData.vm_deploy_args && this.stepFormData.deploy_kubernetes) {
        if (this.stepFormData.selectedVMDocker !== null && this.stepFormData.selectedVMDocker.length !== 0 &&
        this.stepFormData.selectedOSNumber !== null && this.stepFormData.selectedOSNumber.length !== 0 &&
        this.stepFormData.selectedOSType !== null && this.stepFormData.selectedOSType.length !== 0 &&
        this.stepFormData.selectedVMName !== null && this.stepFormData.selectedVMName.length !== 0 &&
        this.stepFormData.selectedMemory !== null && this.stepFormData.selectedMemory.length !== 0 &&
        this.stepFormData.selectedCPUNumber !== null && this.stepFormData.selectedCPUNumber.length !== 0 &&
        this.stepFormData.selectedDisk !== null && this.stepFormData.selectedDisk.length !== 0) {
          return true
        } else {
          this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select a value for VM items', life: 2000 })
          return false
        }
      } else {
        return true
      }
    },
    checkStepWorkloadArgs () {
      if (this.stepFormData.deploy_workload_args) {
        if (this.stepFormData.jenkins_args) {
          if (this.stepFormData.selectedWorkloadName !== null && this.stepFormData.selectedWorkloadName.length !== 0 &&
          this.stepFormData.selectedJSFRepo !== null && this.stepFormData.selectedJSFRepo.length !== 0 &&
          this.stepFormData.selectedCommit !== null && this.stepFormData.selectedCommit.length !== 0 &&
          this.stepFormData.selectedRegistry !== null && this.stepFormData.selectedRegistry.length !== 0) {
            return true
          } else {
            this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select a value for all Jenkins related items', life: 2000 })
            return false
          }
        }
        if (this.stepFormData.workload_package_args) {
          if (this.stepFormData.selectedDeployMode !== null && this.stepFormData.selectedDeployMode.length !== 0 &&
          this.stepFormData.selectedTaskPath !== null && this.stepFormData.selectedTaskPath.length !== 0 &&
          this.stepFormData.selectedPSFRepo !== null && this.stepFormData.selectedPSFRepo.length !== 0 &&
          this.stepFormData.selectedWorkloadArgs !== null && this.stepFormData.selectedWorkloadArgs.length !== 0) {
            return true
          } else {
            this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select a value for all Workload Package related items', life: 2000 })
            return false
          }
        }
        this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select Jenkins or Workload Package', life: 2000 })
        return false
      } else {
        return true
      }
    },
    checkStepSoftwareArgs () {
      if (this.stepFormData.software_package_args) {
        if (this.stepFormData.DPDK) {
          if (this.stepFormData.selectedDPDKArgs === null || this.stepFormData.selectedDPDKArgs.length === 0) {
            this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'DPDK Args', life: 2000 })
            return false
          }
        }
        return true
      } else {
        return true
      }
    },
    checkStepSystemArgs () {
      if (this.stepFormData.system_deploy_args) {
        if (this.stepFormData.os_update) {
          if (this.stepFormData.selectedOS === null || this.stepFormData.selectedOS.length === 0) {
            this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select OS', life: 2000 })
            return false
          }
        }
        if (this.stepFormData.kernel_update) {
          if (this.stepFormData.selectedKernelVersion === null || this.stepFormData.selectedKernelVersion.length === 0) {
            this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select Kernel Version', life: 2000 })
            return false
          }
        }
        if (this.stepFormData.kernel_args_update) {
          if (this.stepFormData.selectedKernelArgs === null || this.stepFormData.selectedKernelArgs.length === 0) {
            this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select Kernel Args', life: 2000 })
            return false
          }
        }
        if (this.stepFormData.bios_update) {
          if (this.stepFormData.selectedBIOSArgs === null || this.stepFormData.selectedBIOSArgs.length === 0) {
            this.$toast.add({ severity: 'error', summary: 'Complete the form', detail: 'Select BIOS Args', life: 2000 })
            return false
          }
        }
        return true
      } else {
        return true
      }
    },
    getWorkers () {
      const endpoint = `/local/api/instance/?controller=${this.selectedController[0].ip}`
      axios
        .get(endpoint)
        .then(response => {
          for (var machine of response.data) {
            machine.label = machine.ip + ',' + machine.instance_type
            this.machine_workers.push(machine)
          }
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    submitProvision () {
      var configsJson = {}
      var machines = []
      // DeployHost
      var deployHost = 'deployHost'
      configsJson[deployHost] = []
      configsJson.platforms = null
      if (this.stepFormData.selectedController != null) {
        for (var host of this.stepFormData.selectedController) {
          configsJson[deployHost].push({ name: 'controller', ansible_host: host.ip, ip: host.ip, username: host.username, hostname: host.hostname === null ? 'default' : host.hostname, password: host.password })
          if (configsJson.platforms === null) {
            configsJson.platforms = host.instance_type === 'CLX' ? 'ICX' : host.instance_type
          }
        }
      }
      if (this.stepFormData.selectedWorker != null) {
        var count = 1
        for (host of this.stepFormData.selectedWorker) {
          configsJson[deployHost].push({ name: 'node' + String(count), ansible_host: host.ip, ip: host.ip, username: host.username, hostname: host.hostname === null ? 'default' : host.hostname, password: host.password })
          count += 1
        }
      }
      for (host of configsJson[deployHost]) {
        machines.push(host.ip)
      }
      // Deploy Kubernetes
      var kubernetesDeploy = 'kubernetes_deploy'
      var kubernetesInstallMethod = 'kubernetesInstallMethod'
      var kubernetesArgs = 'kubernetesArgs'
      var kubeVersion = 'kube_version'
      var kubeNetworkPlugin = 'kube_network_plugin'
      var containerManager = 'container_manager'
      var dashboardEnabled = 'dashboard_enabled'
      var helmEnabled = 'helm_enabled'
      var registryEnabled = 'registry_enabled'
      var ingressNginxEnabled = 'ingress_nginx_enabled'
      var ingressNginxHostNetwork = 'ingress_nginx_host_network'
      var krewEnabled = 'krew_enabled'
      console.log(this.stepFormData)
      configsJson[kubernetesDeploy] = String(this.stepFormData.deploy_kubernetes)
      configsJson[kubernetesInstallMethod] = this.stepFormData.selectedKubernetesInstallMethod ? this.stepFormData.selectedKubernetesInstallMethod.value : ''
      configsJson[kubernetesArgs] = {}
      configsJson[kubernetesArgs][kubeVersion] = this.stepFormData.selectedKubernetesVersion ? this.stepFormData.selectedKubernetesVersion.value : ''
      configsJson[kubernetesArgs][kubeNetworkPlugin] = this.stepFormData.selectedKubernetesNetworkPlugin ? this.stepFormData.selectedKubernetesNetworkPlugin.value : ''
      configsJson[kubernetesArgs][containerManager] = this.stepFormData.selectedContainerManager ? this.stepFormData.selectedContainerManager.value : ''
      configsJson[kubernetesArgs][dashboardEnabled] = this.stepFormData.selectedDashboardEnable ? this.stepFormData.selectedDashboardEnable.value : ''
      configsJson[kubernetesArgs][helmEnabled] = this.stepFormData.selectedHEMLEnable ? this.stepFormData.selectedHEMLEnable.value : ''
      configsJson[kubernetesArgs][registryEnabled] = this.stepFormData.selectedRegistryEnable ? this.stepFormData.selectedRegistryEnable.value : ''
      configsJson[kubernetesArgs][ingressNginxEnabled] = this.stepFormData.selectedIngressNginxEnabled ? this.stepFormData.selectedIngressNginxEnabled.value : ''
      configsJson[kubernetesArgs][ingressNginxHostNetwork] = this.stepFormData.selectedIngressNginxHostNetwork ? this.stepFormData.selectedIngressNginxHostNetwork.value : ''
      configsJson[kubernetesArgs][krewEnabled] = this.stepFormData.selectedKrewEnabled ? this.stepFormData.selectedKrewEnabled.value : ''
      // Deploy Workload
      // var workloadDeploy = 'workload_deploy'
      var jenkins = 'jenkins'
      var workloadName = 'workloadName'
      var jsfRepo = 'jsf_repo'
      var commit = 'commit'
      var registry = 'registry'
      var filterCase = 'filter_case'
      var workloadParameter = 'workload_parameter'
      // var workloadPackage = 'workloadPackage'
      // var deployMode = 'deployMode'
      // var taskPath = 'taskPath'
      // var psfRepo = 'psf_repo'
      // var args = 'args'
      // configsJson[workloadDeploy] = String(this.stepFormData.deploy_workload_args)
      configsJson[jenkins] = String(this.stepFormData.jenkins_args)
      configsJson[workloadName] = this.stepFormData.selectedWorkloadName.name
      configsJson[jsfRepo] = this.stepFormData.selectedJSFRepo
      configsJson[commit] = this.stepFormData.selectedCommit
      configsJson[registry] = this.stepFormData.selectedRegistry ? this.stepFormData.selectedRegistry.value : ''
      configsJson[filterCase] = this.stepFormData.selectedCaseFilter
      configsJson[workloadParameter] = this.stepFormData.selectedWorkloadParameter
      // configsJson[workloadPackage] = String(this.stepFormData.workload_package_args)
      // configsJson[deployMode] = this.stepFormData.selectedDeployMode.value
      // configsJson[taskPath] = this.stepFormData.selectedTaskPath.value
      // configsJson[psfRepo] = this.stepFormData.selectedPSFRepo.value
      // configsJson[args] = this.stepFormData.selectedWorkloadArgs.value
      // Deploy Software
      var softwarePackage = 'softwarepackage'
      var softwarePackageArgs = 'softwarepackageArgs'
      configsJson[softwarePackage] = String(this.stepFormData.software_package_args)
      configsJson[softwarePackageArgs] = []
      if (this.stepFormData.DPDK) {
        configsJson[softwarePackageArgs].push({ Name: 'DPDK', scriptArgs: this.stepFormData.selectedDPDKArgs })
      }
      // Deploy System
      var systemDeploy = 'system_deploy'
      // var osUpdate = 'os_update'
      // var os = 'os'
      var KernelUpdate = 'Kernel_update'
      var kernelVersion = 'kernelVersion'
      var kernelArgsUpdate = 'kernelArgs_update'
      var kernelArgs = 'kernelArgs'
      configsJson[systemDeploy] = String(this.stepFormData.system_deploy_args)
      // configsJson[osUpdate] = String(this.stepFormData.os_update)
      // configsJson[os] = this.stepFormData.selectedOS.value
      configsJson[KernelUpdate] = String(this.stepFormData.kernel_update)
      configsJson[kernelVersion] = this.stepFormData.selectedKernelVersion ? this.stepFormData.selectedKernelVersion.value : ''
      configsJson[kernelArgsUpdate] = String(this.stepFormData.kernel_args_update)
      configsJson[kernelArgs] = this.stepFormData.selectedKernelArgs ? this.stepFormData.selectedKernelArgs.value : ''
      // Deploy VM
      var vmDeploy = 'vm_deploy'
      var vmDocker = 'vm_docker'
      var vmosArgs = 'vmosArgs'
      var osNumber = 'osNumber'
      var osType = 'osType'
      var vmName = 'vmName'
      var memory = 'memory'
      var cpuNumber = 'cpuNumber'
      var disk = 'disk'
      configsJson[vmDeploy] = String(this.stepFormData.vm_deploy_args && this.stepFormData.deploy_kubernetes)
      configsJson[vmDocker] = this.stepFormData.selectedVMDocker ? this.stepFormData.selectedVMDocker.value : ''
      configsJson[vmosArgs] = {}
      configsJson[vmosArgs][osNumber] = this.stepFormData.selectedOSNumber ? this.stepFormData.selectedOSNumber.value : ''
      configsJson[vmosArgs][osType] = this.stepFormData.selectedOSType ? this.stepFormData.selectedOSType.value : ''
      configsJson[vmosArgs][vmName] = this.stepFormData.selectedVMName
      configsJson[vmosArgs][memory] = this.stepFormData.selectedMemory ? this.stepFormData.selectedMemory.value : ''
      configsJson[vmosArgs][cpuNumber] = this.stepFormData.selectedCPUNumber ? this.stepFormData.selectedCPUNumber.value : ''
      configsJson[vmosArgs][disk] = this.stepFormData.selectedDisk ? this.stepFormData.selectedDisk.value : ''
      // Email
      var sender = 'sender'
      var receivers = 'receivers'
      configsJson[sender] = this.stepFormData.SenderEmail
      configsJson[receivers] = this.stepFormData.ReceiverEmail
      configsJson = JSON.stringify(configsJson)
      // console.log(configsJson)
      // if (this.$v.$invalid) {
      var con = false
      if (con) {
        alert('Please fill the mandatory info')
      } else {
        const endpoint = '/local/api/provision/'
        const config = {
          headers: {
            'content-type': 'application/json',
            'X-CSRFTOKEN': CSRF_TOKEN
          }
        }
        const data = {
          workload: this.stepFormData.selectedWorkloadName.name,
          config_version: this.stepFormData.selectedVersion.version,
          config_json: configsJson,
          machines: machines,
          start_time: this.stepFormData.selectedDatetime[0],
          end_time: this.stepFormData.selectedDatetime[1]
        }
        axios
          .post(endpoint, data, config)
          .then(response => {
            this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Provision success', life: 3000 })
            this.$router.push('job')
          })
          .catch(e => {
            // console.log(e.response.data)
            this.$toast.add({ severity: 'error', summary: 'Failed', detail: e.response.data, life: 10000 })
            this.errors.push(e)
          })
      }
    },
    getworkloads () {
      const endpoint = '/local/api/workload/'
      axios
        .get(endpoint)
        .then(response => {
          this.stepFormData.Workloads = response.data
          this.stepFormData.selectedWorkload = 'qat'
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    getMachines () {
      const endpoint = '/local/api/instance/'
      axios
        .get(endpoint)
        .then(response => {
          this.stepFormData.MachineControllers = []
          this.stepFormData.MachineWorkers = []
          for (var machine of response.data) {
            machine.instance_type.toUpperCase()
            machine.show_name = machine.ip + ' - ' + machine.instance_type
            if (machine.k8s_role === 'controller,worker') {
              this.stepFormData.MachineControllers.push(machine)
              this.stepFormData.MachineWorkers.push(machine)
            } else if (machine.k8s_role === 'worker') {
              this.stepFormData.MachineWorkers.push(machine)
            } else if (machine.k8s_role === 'controller') {
              this.stepFormData.MachineControllers.push(machine)
            }
          }
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    getAllConfigs () {
      const endpoint = '/local/api/provison_parameter/'
      axios
        .get(endpoint)
        .then(response => {
          // StepKubernetes
          this.stepFormData.KubernetesInstallMethod = response.data.kubernetes.kubernetesInstallMethod
          this.stepFormData.KubernetesVersion = response.data.kubernetes.kube_version
          this.stepFormData.KubernetesNetworkPlugin = response.data.kubernetes.kube_network_plugin
          this.stepFormData.ContainerManager = response.data.kubernetes.container_manager
          this.stepFormData.DashboardEnable = response.data.kubernetes.dashboard_enabled
          this.stepFormData.HEMLEnable = response.data.kubernetes.helm_enabled
          this.stepFormData.RegistryEnable = response.data.kubernetes.registry_enabled
          this.stepFormData.IngressNginxEnabled = response.data.kubernetes.ingress_nginx_enabled
          this.stepFormData.IngressNginxHostNetwork = response.data.kubernetes.ingress_nginx_host_network
          this.stepFormData.KrewEnabled = response.data.kubernetes.krew_enabled
          // StepWorkloadArgs
          this.stepFormData.WorkloadName = []
          this.stepFormData.JSFRepo = response.data.workload.jsf_repo
          this.stepFormData.Commit = response.data.workload.commit
          this.stepFormData.Registry = response.data.workload.registry
          this.stepFormData.DeployMode = response.data.workload.deployMode
          this.stepFormData.TaskPath = response.data.workload.taskPath
          this.stepFormData.PSFRepo = response.data.workload.psf_repo
          this.stepFormData.WorkloadArgs = response.data.workload.args
          // StepSystemArgs
          this.stepFormData.OS = response.data.system.os
          this.stepFormData.KernelVersion = response.data.system.kernelVersion
          this.stepFormData.KernelArgs = response.data.system.kernelArgs
          this.stepFormData.BIOSArgs = response.data.system.biosArgs
          this.stepFormData.BIOSArgsMapping = response.data.system.valueMapping
          // StepVMArgs
          this.stepFormData.VMDocker = response.data.vm.vm_docker
          this.stepFormData.OSNumber = response.data.vm.osNumber
          this.stepFormData.OSType = response.data.vm.osType
          this.stepFormData.VMName = response.data.vm.vmName
          this.stepFormData.Memory = response.data.vm.memory
          this.stepFormData.CPUNumber = response.data.vm.cpuNumber
          this.stepFormData.Disk = response.data.vm.disk
          // StepEmail
          this.stepFormData.SenderEmail = response.data.email.sender.value
          this.stepFormData.ReceiverEmail = response.data.email.receivers.value
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    }
  },
  created () {
    this.getworkloads()
    this.getMachines()
    this.getAllConfigs()
  }
}
</script>
