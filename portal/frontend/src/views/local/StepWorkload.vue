<template>
  <div align="center">
  <div class="p-field p-col-6 p-md-6 text-align-left">
    <el-card class="box-card" style="height: 500px;">
      <div slot="header" class="clearfix">
        <span>Workload</span>
      </div>
      <div>
        <el-form label-position="right" label-width="80px" :model="formData">
          <div class="p-formgroup-inline">
            <div class="p-field p-col-5">
              <h5>Workload</h5>
              <Dropdown
                v-model="selectedWorkload"
                :options="formData.Workloads"
                optionLabel="name"
                placeholder="Workload to choose..."
                :filter="true"
                :showClear="true"
              />
            </div>
            <div class="p-field p-col-5">
              <h5>Version</h5>
              <Dropdown
                v-model="selectedVersion"
                :options="formData.Versions"
                optionLabel="version"
                placeholder="Version to provision..."
                :filter="true"
                :showClear="true"
              />
            </div>
          </div>
        </el-form>
      </div>
    </el-card>
  </div>
  </div>
</template>
<script>
import Dropdown from 'primevue/dropdown'
import axios from 'axios'
export default {
  components: {
    Dropdown
  },
  data () {
    return {
      selectedWorkload: this.formData.selectedWorkloadName,
      selectedVersion: this.formData.selectedVersion
    }
  },
  props: {
    formData: Object
  },
  methods: {
    getVersions () {
      const endpoint = '/local/api/workload_system_config/?workload_id=' + this.selectedWorkload.id + '&version_info=true'
      axios
        .get(endpoint)
        .then(response => {
          this.formData.Versions = response.data
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    getConfigs () {
      const endpoint = '/local/api/parameters/?workload_id=' + this.selectedWorkload.id + '&version=' + this.selectedVersion.version
      axios
        .get(endpoint)
        .then(response => {
          this.configs = response.data
          for (var conf of this.configs) {
            // StepKubernetes
            if (conf.parameter === 'kubernetesInstallMethod') {
              if (conf.value !== null) {
                this.formData.selectedKubernetesInstallMethod = { value: conf.value }
                if (conf.value === 'vm') {
                  this.formData.vm_deploy_args = true
                } else {
                  this.formData.vm_deploy_args = false
                }
              }
            }
            if (conf.parameter === 'kube_version') {
              if (conf.value !== null) {
                this.formData.selectedKubernetesVersion = { value: conf.value }
              }
            }
            if (conf.parameter === 'kube_network_plugin') {
              if (conf.value !== null) {
                this.formData.selectedKubernetesNetworkPlugin = { value: conf.value }
              }
            }
            if (conf.parameter === 'container_manager') {
              if (conf.value !== null) {
                this.formData.selectedContainerManager = { value: conf.value }
              }
            }
            if (conf.parameter === 'dashboard_enabled') {
              if (conf.value !== null) {
                this.formData.selectedDashboardEnable = { value: conf.value }
              }
            }
            if (conf.parameter === 'helm_enabled') {
              if (conf.value !== null) {
                this.formData.selectedHEMLEnable = { value: conf.value }
              }
            }
            if (conf.parameter === 'registry_enabled') {
              if (conf.value !== null) {
                this.formData.selectedRegistryEnable = { value: conf.value }
              }
            }
            if (conf.parameter === 'ingress_nginx_enabled') {
              if (conf.value !== null) {
                this.formData.selectedIngressNginxEnabled = { value: conf.value }
              }
            }
            if (conf.parameter === 'ingress_nginx_host_network') {
              if (conf.value !== null) {
                this.formData.selectedIngressNginxHostNetwork = { value: conf.value }
              }
            }
            if (conf.parameter === 'krew_enabled') {
              if (conf.value !== null) {
                this.formData.selectedKrewEnabled = { value: conf.value }
              }
            }
            // StepWorkloadArgs
            if (conf.parameter === 'workload_deploy') {
              if (conf.value !== null) {
                this.formData.deploy_workload_args = conf.value === 'true'
              }
            }
            if (conf.parameter === 'jsf_repo') {
              if (conf.value !== null) {
                this.formData.selectedJSFRepo = conf.value
              }
            }
            if (conf.parameter === 'commit') {
              if (conf.value !== null) {
                this.formData.selectedCommit = conf.value
              }
            }
            if (conf.parameter === 'registry') {
              if (conf.value !== null) {
                this.formData.selectedRegistry = { value: conf.value }
              }
            }
            if (conf.parameter === 'deployMode') {
              if (conf.value !== null) {
                this.formData.selectedDeployMode = { value: conf.value }
              }
            }
            if (conf.parameter === 'taskPath') {
              if (conf.value !== null) {
                this.formData.selectedTaskPath = conf.value
              }
            }
            if (conf.parameter === 'psf_repo') {
              if (conf.value !== null) {
                this.formData.selectedPSFRepo = { value: conf.value }
              }
            }
            if (conf.parameter === 'args') {
              if (conf.value !== null) {
                this.formData.selectedWorkloadArgs = [{ value: conf.value }]
              }
            }
            // StepSystermArgs
            if (conf.parameter === 'os') {
              if (conf.value !== null) {
                this.formData.selectedOS = { value: conf.value }
              }
            }
            if (conf.parameter === 'Kernel_update') {
              if (conf.value !== null) {
                this.formData.kernel_update = conf.value === 'true'
              }
            }
            if (conf.parameter === 'kernelVersion') {
              if (conf.value !== null) {
                this.formData.selectedKernelVersion = { value: conf.value }
              }
            }
            if (conf.parameter === 'kernelArgs_update') {
              if (conf.value !== null) {
                this.formData.kernel_args_update = conf.value === 'true'
              }
            }
            if (conf.parameter === 'kernelArgs') {
              if (conf.value !== null) {
                this.formData.selectedKernelArgs = { value: conf.value }
              }
            }
            if (conf.parameter === 'bios_update') {
              if (conf.value !== null) {
                this.formData.bios_update = conf.value === 'true'
              }
            }
            if (conf.parameter === 'biosArgs') {
              if (conf.value !== null) {
                this.formData.selectedBIOSArgs = []
                for (var val of conf.value.split(',')) {
                  this.formData.selectedBIOSArgs.push({ value: val })
                }
              }
            }
            // StepVMArgs
            if (conf.parameter === 'vm_docker') {
              if (conf.value !== null) {
                this.formData.selectedVMDocker = { value: conf.value }
              }
            }
            if (conf.parameter === 'osNumber') {
              if (conf.value !== null) {
                this.formData.selectedOSNumber = { value: conf.value }
              }
            }
            if (conf.parameter === 'osType') {
              if (conf.value !== null) {
                this.formData.selectedOSType = { value: conf.value }
              }
            }
            if (conf.parameter === 'vmName') {
              if (conf.value !== null) {
                this.formData.selectedVMName = conf.value
              }
            }
            if (conf.parameter === 'memory') {
              if (conf.value !== null) {
                this.formData.selectedMemory = { value: conf.value }
              }
            }
            if (conf.parameter === 'cpuNumber') {
              if (conf.value !== null) {
                this.formData.selectedCPUNumber = { value: conf.value }
              }
            }
            if (conf.parameter === 'disk') {
              if (conf.value !== null) {
                this.formData.selectedDisk = { value: conf.value }
              }
            }
            // StepEmail
            if (conf.parameter === 'sender') {
              if (conf.value !== null) {
                this.formData.SenderEmail = conf.value
              }
            }
            if (conf.parameter === 'receivers') {
              if (conf.value !== null) {
                this.formData.ReceiverEmail = conf.value
              }
            }
          }
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    }
  },
  watch: {
    selectedWorkload: function () {
      this.formData.WorkloadName = [this.selectedWorkload]
      this.formData.selectedWorkloadName = this.selectedWorkload
      if (this.selectedWorkload !== null && this.selectedWorkload.length !== 0) {
        this.getVersions()
      }
    },
    selectedVersion: function () {
      if (this.selectedVersion !== null && this.selectedVersion.length !== 0) {
        this.getConfigs()
        this.formData.selectedVersion = this.selectedVersion
      }
    }
  }
}
</script>

<style scoped>
.text-align-left {
  text-align: left;
}
</style>
