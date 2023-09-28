<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <div class="grid">
      <Accordion :multiple="true" :activeIndex="[0,1,2,3,4]">
          <AccordionTab v-for="tab in tabs" :key="tab.title" :header="tab.title">
              <div v-if="tab.content === 'Workload'">
                <div class="p-formgroup-inline">
                  <div class="col">
                    <h5>Workload:</h5>
                    <Dropdown
                      v-tooltip="'What workload to validate'"
                      v-model="workload.selectedWorkload"
                      :options="workload.allWorkloads"
                      optionLabel="name"
                      placeholder="Workload to choose..."
                      :filter="true"
                      :showClear="true"
                    />
                     <InlineMessage v-if="!workload.selectedWorkload">Required</InlineMessage>
                  </div>
                  <div class="col">
                    <h5>Configuration Version:</h5>
                    <Dropdown
                      v-tooltip="'Workload configs, including WSF_repository/Registry/revision by default.'"
                      v-model="workload.selectedVersion"
                      :options="workload.versions"
                      optionLabel="version"
                      placeholder="Version to provision..."
                      :filter="true"
                      :showClear="true"
                    />
                     <InlineMessage v-if="!workload.selectedVersion">Required</InlineMessage>
                  </div>
                  <div class="col-5"></div>
                </div>
              </div>

              <div v-if="tab.content === 'Host' && workload.selectedWorkload && workload.selectedVersion">
                <div class="p-formgroup-inline">
                    <div class="col-3">
                      <h5>Kubernetes Install Options:</h5>
                    </div>
                      <div class="col">
                        <h5>Host:</h5>
                        <div>
                            <InputSwitch v-model="hosts.k8sHostInstall" v-tooltip="'Enable kubernetes to install on hosts'"/>
                        </div>
                      </div>
                    <div class="col">
                        <h5>VM:</h5>
                        <div>
                            <!-- <InputSwitch v-model="hosts.k8sVMInstall" v-tooltip="'Enable kubernetes to install on Linux KVM'"/> -->
                            <InputSwitch model="false" v-tooltip="'On developing'"/>
                            <InlineMessage v-if="hosts.k8sVMInstall">Not supported yet</InlineMessage>
                        </div>
                    </div>
                  <div class="col-5"></div>
                </div>
                <div v-if="hosts.k8sHostInstall">
                    <div class="p-formgroup-inline">
                      <div class="col">
                        <h5>Kubernetes Controller:</h5>
                        <Dropdown
                          v-tooltip="'Choose one host as kubernetes controller'"
                          v-model="hosts.selectedController"
                          :options="hosts.machineControllers"
                          optionLabel="show_name"
                          placeholder="Controller to provision..."
                          :filter="true"
                          :showClear="true"
                        />
                        <InlineMessage v-if="!hosts.selectedController">Required</InlineMessage>
                      </div>
                      <div class="col">
                        <h5>Kubernetes Workers:</h5>
                        <MultiSelect
                          v-model="hosts.selectedWorker"
                          :options="hosts.machineWorkers"
                          optionLabel="show_name"
                          placeholder="Workers to provision..."
                          :filter="true"
                          :showClear="true"
                          v-tooltip="'Choose one or more hosts as kubernetes worker'"
                        />
                        <InlineMessage v-if="hosts.selectedWorker.length === 0">Required</InlineMessage>
                      </div>
                      <div class="col">
                        <h5>Schedule Time:</h5>
                        <div class="card" style="width: 80%;">
                            <Calendar v-model="hosts.selectedDatetime" 
                              selectionMode="range" 
                              :showTime="true" 
                              showButtonBar 
                              :manualInput="false"
                              :showSeconds="true"
                              v-tooltip="'Time that to start workload, should not overlap with exists running or in_queue workload.'"
                            />
                        <InlineMessage v-if="hosts.dateInValidated">Required, please ensure valid start and end range</InlineMessage>
                        </div>
                      </div>
                    </div>
                    <div v-if="hosts.conflictedWorkers.length !== 0">
                        <InlineMessage v-if="hosts.conflictedWorkers.length !== 0">Resolve confilcits is required, please make sure no job already occupied the machine </InlineMessage>
                      <DataTable class="font table" responsiveLayout="scroll" :value='hosts.conflictedWorkers' columnResizeMode="fit" v-tooltip="'conflicted jobs info'"
                        :paginator='true' :rows='20'
                        paginatorTemplate='CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown'
                        :rowsPerPageOptions='[20, 50, 100]' currentPageReportTemplate='Showing {first} to {last} of {totalRecords}'>
                        <template #empty>
                          No conflict hosts found.
                        </template>
                        <template #loading>
                          Loading conflict hosts data. Please wait.
                        </template>
                        <Column v-for="col of columns" :field="col.field" :header="col.header" :key="col.field"> 
                          <template #body="slotProps" v-if="col.field === 'start_time'">
                            <div>{{ slotProps.data.start_time.slice(0,19).replace('T',' ') }}</div>
                          </template>
                          <template #body="slotProps" v-else-if="col.field === 'end_time'">
                            <div>{{ slotProps.data.end_time.slice(0,19).replace('T',' ') }}</div>
                          </template>
                        </Column>
                      </DataTable>
                    </div>
                </div>
                <div v-if="hosts.k8sVMInstall">
                  <div class="p-formgroup-inline">
                    <div class="col">
                      <h5>KVM Hosts:</h5>
                      <MultiSelect
                        v-model="hosts.selectedKVMHosts"
                        :options="hosts.KVMHosts"
                        placeholder="kvm hosts to provision..."
                        optionLabel="show_name"
                        :filter="true"
                        :showClear="true"
                        v-tooltip="'Linux hosts that support KVM'"
                      />
                      <InlineMessage v-if="hosts.dateInValidated">Required</InlineMessage>
                    </div>
                    <div class="col">
                      <h5>Schedule Time:</h5>
                      <div class="card" style="width: 80%;">
                          <Calendar v-model="hosts.selectedDatetime" 
                            selectionMode="range" 
                            :showTime="true" 
                            showButtonBar 
                            :manualInput="false"
                            :showSeconds="true"
                            v-tooltip="'Time that to start workload.'"
                          />
                        <InlineMessage v-if="hosts.dateInValidated">Required</InlineMessage>
                      </div>
                    </div>
                    <div class="col"></div>
                  </div>
                  <!-- <div v-if="hosts.conflictedWorkers.length !== 0">
                      <InlineMessage v-if="hosts.conflictedWorkers.length !== 0">Resolve confilcits is required, please make sure no job already occupied the machine </InlineMessage>
                      <DataTable class="font table" responsiveLayout="scroll" :value='hosts.conflictedWorkers' columnResizeMode="fit" v-tooltip="'Conficted hosts'"
                        :paginator='true' :rows='20'
                        paginatorTemplate='CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown'
                        :rowsPerPageOptions='[20, 50, 100]' currentPageReportTemplate='Showing {first} to {last} of {totalRecords}'>
                        <template #empty>
                          No conflict hosts found.
                        </template>
                        <template #loading>
                          Loading conflict hosts data. Please wait.
                        </template>
                        <Column v-for="col of columns" :field="col.field" :header="col.header" :key="col.field"> 
                        </Column>
                      </DataTable>
                  </div> -->
                  </div>
                </div>

              <div v-if="tab.content === 'HostParams'">
                <div v-if="hosts.k8sHostInstall && workload.selectedWorkload && workload.selectedVersion">
                    <div class="col">
                        <h5>Reset kubernetes:</h5>
                        <div>
                            <InputSwitch v-model="args.reset_k8s"  v-tooltip="'Reset k8s no matter k8s is installed or not.'"/>
                        </div>
                    </div>
                </div>
                <div v-if="hosts.k8sVMInstall">
                  <div class="p-formgroup-inline">
                      <div class="col">
                        <h5>VM Docker:</h5>
                        <Dropdown
                          v-tooltip="'Using docker as VM backend'"
                          v-model="hosts.selectedVmDocker"
                          :options="hosts.vmDocker"
                          placeholder="Workers to provision..."
                          optionLabel="value"
                          :filter="true"
                          :showClear="true"
                        />
                      </div>
                      <div class="col">
                        <h5>OS Number:</h5>
                        <Dropdown
                          v-tooltip="'OS number'"
                          v-model="hosts.selectedVmOSNumber"
                          :options="hosts.vmOSNumber"
                          placeholder="Controller to provision..."
                          optionLabel="value"
                          :filter="true"
                          :showClear="true"
                        />
                      </div>
                      <div class="col">
                        <h5>OS Type:</h5>
                        <Dropdown
                          v-tooltip="'OS type'"
                          v-model="hosts.selectedVmOSType"
                          :options="hosts.vmOSType"
                          placeholder="Workers to provision..."
                          optionLabel="value"
                          :filter="true"
                          :showClear="true"
                        />
                      </div>
                      <div class="col">
                        <h5>VM Name:</h5>
                        <InputText type="text" v-model="hosts.vmName"  v-tooltip="'Customed VM name'"/>
                      </div>
                  </div>
                  <div class="p-formgroup-inline">
                      <div class="col">
                        <h5>Memory:</h5>
                        <Dropdown
                          v-tooltip="'Memory that need to allot'"
                          v-model="hosts.selectedVmMemory"
                          :options="hosts.vmMemory"
                          placeholder="Controller to provision..."
                          optionLabel="value"
                          :filter="true"
                          :showClear="true"
                        />
                      </div>
                      <div class="col">
                        <h5>CPU Number:</h5>
                        <Dropdown
                          v-tooltip="'Cpu quantity that need to allot'"
                          v-model="hosts.selectedVmCPUNumber"
                          :options="hosts.vmCPUNumber"
                          placeholder="Workers to provision..."
                          optionLabel="value"
                          :filter="true"
                          :showClear="true"
                        />
                      </div>
                      <div class="col">
                        <h5>Disk:</h5>
                        <Dropdown
                          v-tooltip="'Disk storage that need to allot'"
                          v-model="hosts.selectedVmDisk"
                          :options="hosts.vmDisk"
                          placeholder="Workers to provision..."
                          optionLabel="value"
                          :filter="true"
                          :showClear="true"
                        />
                      </div>
                      <div class="col"></div>
                  </div>
                </div>
              </div>

              <div v-if="tab.content === 'Args' && hosts.selectedController && hosts.selectedWorker.length !== 0">
                <div class="p-formgroup-inline">
                  <div class="col">
                    <h5>WSF Repository:</h5>
                    <InputText :ref="workload.configs" v-model="workload.configs.jsf_repo" type="text" placeholder="WSF_repo"  v-tooltip="'WSF repositry, default is https://github.com/intel/workload-services-framework.git'">
                    </InputText>
                     <InlineMessage v-if="!workload.configs.jsf_repo">Required</InlineMessage>
                  </div>
                  <div class="col">
                    <h5>Registry:</h5>
                    <Dropdown
                      v-tooltip="'Registry that default to use'"
                      v-model="workload.selectedRegistry"
                      :options="workload.configs.registry"
                      placeholder="reigstry to provision..."
                      :filter="true"
                      :showClear="true"
                    />
                  </div>
                  <div class="col">
                    <h5>Revision:</h5>
                    <InputText v-model="workload.configs.commit" type="text" placeholder="commit"  v-tooltip="'Git hub commit'">
                    </InputText>
                     <InlineMessage v-if="!workload.configs.commit">Required</InlineMessage>
                  </div>
                </div>
                <div class="p-formgroup-inline">
                  <div class="col">
                    <h5>Case Filter:</h5>
                    <InputText v-model="workload.configs.filter_case" type="text" placeholder="case filter"  v-tooltip="'Which case to run, such as pkm is that case name contains pkm, if leave blank all tests will be ran. Support regular expression'">
                    </InputText>
                  </div>
                  <div class="col">
                    <h5>Exclude Case:</h5>
                    <InputText v-model="workload.configs.exclude_case" type="text" placeholder="exclude case"  v-tooltip="'Which case do not run, such as gated is that case name do not contains gated, if leave blank all tests will not be excluded. Support regular expression'">
                    </InputText>
                  </div>
                  <div class="col">
                    <h5>Workload Parameters:</h5>
                    <InputText v-model="workload.configs.workload_parameter" type="text" placeholder="woarkload parameters"  v-tooltip="'Workload runtime parameters, such as REQUESTS=1000 for Nginx, more parameters refer to workload\'s readme'">
                  </InputText>
                  </div>
                </div>
                <div class="p-formgroup-inline">
                  <div class="col">
                    <h5>Ctest Options:</h5>
                    <InputText v-model="workload.configs.ctest_option" type="text" placeholder="ctest option"  v-tooltip="'ctest.sh options like --loop to run the ctest commands sequentially.'">
                    </InputText>
                  </div>
                </div>
                <div class="col" v-if="workload.selectedWorkload.name === 'Smart-Sport-Analyzer'">
                  <h5>Upload video files</h5>
                  <div class="card flex justify-content-center col-4">
                      <FileUpload name="files" url="/local/api/upload_video_check/" accept="video/*" :maxFileSize="1000000000" 
                      @before-send="submitUpload" :multiple="true" />
                  </div>
                </div>
              </div>
              <div v-if="tab.content === 'Notification'">
                <div class="p-formgroup-inline">
                  <div class="col">
                    <h5>SMTP Server:</h5>
                    <InputText v-model="workload.configs.smtp_server" type="text" placeholder="SMTP server"  v-tooltip="'Email\'s SMTP server and port'"></InputText>
                     <InlineMessage severity="info" style="background: rgb(0, 199, 253);">Optional</InlineMessage>
                  </div> 
                  <div class="col">
                    <h5>Sender Email:</h5>
                    <InputText v-model="workload.configs.sender" type="text" placeholder="sender"  v-tooltip="'Email that who would send the info'"></InputText>
                     <InlineMessage severity="info" style="background: rgb(0, 199, 253);">Optional</InlineMessage>
                  </div> 
                 
                  <div class="col">
                    <h5>Receivers Email:</h5>
                    <InputText v-model="workload.configs.receivers" type="text" placeholder="receivers"  v-tooltip="'Emails that who would receive the infon'"></InputText>
                     <InlineMessage severity="info" style="background: rgb(0, 199, 253);">Optional</InlineMessage>
                  </div>
                  <div class="col"></div>
                </div>
              </div>
          </AccordionTab>
      </Accordion>
      <div v-if="hosts.selectedController && hosts.selectedWorker.length !== 0 && hosts.conflictedWorkers.length === 0">
        <Button label="Submit" style="width:8rem;float:right;" @click="submitProvision"  v-tooltip="'Submit that workload configs to jobs.'"></Button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { CSRF_TOKEN } from '../../common/csrf_token'
import Button from 'primevue/button';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Calendar from 'primevue/calendar';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputSwitch from 'primevue/inputswitch';
import InputText from 'primevue/inputtext';
import InlineMessage from 'primevue/inlinemessage';
import Tooltip from 'primevue/tooltip';
import Tag from 'primevue/tag'
import FileUpload from 'primevue/fileupload';

export default {
  components: {
    Button,
    Accordion,
    AccordionTab,
    Dropdown,
    MultiSelect,
    Calendar,
    DataTable,
    Column,
    InputSwitch,
    InputText,
    InlineMessage,
    Tooltip,
    Tag,
    FileUpload
  },
  data() {
    return {
      workload: {
        selectedWorkload: null,
        selectedVersion: null,
        selectedRegistry: null,
        configs: {
          "jsf_repo": null,
          "registry": [],
          "commit": null,
          "filter_case": null,
          "exclude_case": null,
          "ctest_option": null,
          "workload_parameter": null,
        },
        allWorkloads: [],
        versions: [],
      },
      hosts: {
        selectedController: null,
        selectedWorker: [],
        machineControllers: [],
        machineWorkers: [],
        selectedDatetime: [new Date((new Date()).getTime()), new Date((new Date()).getTime() + 3600000)],
        dateInValidated: false,
        conflictedWorkers: [],
        k8sHostInstall: true,
        k8sVMInstall: false,

        vmCPUNumber: [],
        vmDisk: [],
        vmMemory: [],
        vmOSType: [],
        vmOSNumber: [],
        vmName: "",
        vmDeploy: [],
        vmDocker: [],
        selectedVmCPUNumber: "",
        selectedVmDisk: "",
        selectedVmMemory: "",
        selectedVmOSType: "",
        selectedVmOSNumber: "",
        selectedVmDeploy: "",
        selectedVmDocker: "",
        selectedKVMHosts: [],
        KVMHosts: [],

      },
      args: {
        reset_k8s: false,
      },
      columns: null,
      errors: [],
      tabs: [
        { title: 'Choose Workload', content: 'Workload' },
        { title: 'Choose Hosts', content: 'Host' },
        { title: 'Host Parameters', content: 'HostParams' },
        { title: 'Benchmark Parameters', content: 'Args' },
        { title: 'Notification Parameters', content: 'Notification' }
      ],
    }
  },
  methods: {
    getWorkers() {
      const endpoint = `/local/api/instance/?controller=${this.hosts.selectedController[0].ip}`
      axios
        .get(endpoint)
        .then(response => {
          for (var machine of response.data) {
            machine.label = machine.ip + ',' + machine.instance_type
            this.hosts.machineWorkers.push(machine)
          }
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    submitProvision() {
      var configsJson = {"deployHost": []}
      var machines = []
      if (this.hosts.selectedWorker && this.hosts.selectedController) {
        let host = this.hosts.selectedController
        configsJson["deployHost"].push({ name: 'controller', ansible_host: host.ip, ip: host.ip, username: host.username, hostname: host.hostname === null ? 'default' : host.hostname, password: "***" })
        var count = 1
        for (host of this.hosts.selectedWorker) {
          configsJson["deployHost"].push({ name: 'node' + String(count), ansible_host: host.ip, ip: host.ip, username: host.username, hostname: host.hostname === null ? 'default' : host.hostname, password: "***" })
          configsJson.platforms = host.instance_type === 'CLX' ? 'ICX' : host.instance_type
          count += 1
        }
      for (host of configsJson["deployHost"]) {
        machines.push(host.ip)
      }
      }
      configsJson["kubernetes_deploy"] = String(this.args.reset_k8s)
      configsJson["jenkins"] = String(true)
      configsJson["workloadName"] = this.workload.selectedWorkload.name
      configsJson["jsf_repo"] = this.workload.configs.jsf_repo
      configsJson["commit"] = this.workload.configs.commit
      configsJson["registry"] = this.workload.selectedRegistry
      configsJson["filter_case"] = this.workload.configs.filter_case
      configsJson["ctest_option"] = this.workload.configs.ctest_option ? this.workload.configs.ctest_option: 'default'
      configsJson["exclude_case"] = this.workload.configs.exclude_case ? this.workload.configs.exclude_case :'default' 
      configsJson["workload_parameter"] = this.workload.configs.workload_parameter? this.workload.configs.workload_parameter: ""
      // Email
      configsJson["smtp"] = this.workload.configs.smtp_server ? this.workload.configs.smtp_server : "default"
      configsJson["sender"] = this.workload.configs.sender ? this.workload.configs.sender : "default@default.com"
      configsJson["receivers"] = this.workload.configs.receivers ? this.workload.configs.receivers : "default@default.com"
      configsJson["kubernetesInstallMethod"] = String(this.hosts.k8sHostInstall) ? "host" : "vm"
      configsJson["vm_deploy"] = String(this.hosts.k8sVMInstall)
      configsJson["vm_docker"] = ""
      configsJson["softwarepackage"] = String("false")
      configsJson["softwarepackageArgs"] = []
      configsJson["system_deploy"] = String("false")
      configsJson["Kernel_update"] = String("false")
      configsJson["kernelVersion"] = ""
      configsJson["kernelArgs_update"] = String("false")
      configsJson["kernelArgs"] = ""
      configsJson["vmosArgs"] = {
        "osNumber": this.hosts.selectedVmOSNumber, "osType": this.hosts.selectedVmOSType,
        "vmName": this.hosts.vmName, "memory": this.hosts.selectedVmMemory,
        "cpuNumber": this.hosts.selectedVmCPUNumber, "disk": this.hosts.selectedVmDisk
      }


      configsJson = JSON.stringify(configsJson)
      console.log(configsJson)
      // if (this.$v.$invalid) {
      if (this.hosts.conflictedWorkers.length !== 0) {
        alert('Please resolve the conflicted hosts first.')
      } else {
        const endpoint = '/local/api/provision/'
        const config = {
          headers: {
            'content-type': 'application/json',
            'X-CSRFTOKEN': CSRF_TOKEN
          }
        }
        const data = {
          workload: this.workload.selectedWorkload.name,
          config_version: this.workload.selectedVersion.version,
          config_json: configsJson,
          machines: machines,
          schedule_time: this.hosts.selectedDatetime,
        }
        axios
          .post(endpoint, data, config)
          .then(response => {
            this.$router.push('job')
          })
          .catch(e => {
            this.errors.push(e)
            console.log(e.response)
            alert(e.response.data)
          })
      }
    },
    getworkloads() {
      const endpoint = '/local/api/workload/'
      axios
        .get(endpoint)
        .then(response => {
          this.workload.allWorkloads = response.data
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    getMachines() {
      const endpoint = '/local/api/instance/'
      axios
        .get(endpoint)
        .then(response => {
          this.hosts.machineControllers = []
          this.hosts.machineWorkers = []
          this.hosts.KVMHosts = []
          for (var machine of response.data) {
            machine.instance_type.toUpperCase()
            machine.show_name = machine.ip + ' - ' + machine.instance_type
            this.hosts.KVMHosts.push(machine)
            if (machine.k8s_role === 'controller,worker') {
              this.hosts.machineControllers.push(machine)
              this.hosts.machineWorkers.push(machine)
            } else if (machine.k8s_role === 'worker') {
              this.hosts.machineWorkers.push(machine)
            } else if (machine.k8s_role === 'controller') {
              this.hosts.machineControllers.push(machine)
            }
          }
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    getVersions() {
      const endpoint = '/local/api/workload_system_config/?workload_id=' + this.workload.selectedWorkload.id + '&version_info=true'
      axios
        .get(endpoint)
        .then(response => {
          this.workload.versions = response.data
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    getWorkloadConfigs() {
      const endpoint = '/local/api/parameters/?workload_id=' + this.workload.selectedWorkload.id + '&version=' + this.workload.selectedVersion.version
      axios
        .get(endpoint)
        .then(response => {
          // console.log(response.data)
          let configs = {}
          for (const config of response.data) {
            configs[config.parameter] = config.value
          }
            configs["registry"] = configs["registry"].split(",")
            configs["filter_case"] = "pkm"
            configs["exclude_case"] = ""
            configs["ctest_option"] = ""
            configs["smtp_server"] = "smtp.xxx.com:25"
            this.workload.selectedRegistry = configs["registry"][0]
            this.workload.configs = configs
        })
    },
    getVMconfigs() {
      const endpoint = '/local/api/provison_parameter/'
      axios
        .get(endpoint)
        .then(response => {
          console.log(response.data)
          this.hosts.vmDocker = response.data.vm.vm_docker
          this.hosts.vmOSNumber = response.data.vm.osNumber
          this.hosts.vmOSType = response.data.vm.osType
          this.hosts.vmMemory = response.data.vm.memory
          this.hosts.vmCPUNumber = response.data.vm.cpuNumber
          this.hosts.vmDisk = response.data.vm.disk
        })
    },
    checkWorkerSchedule() {
      this.hosts.dateInValidated = true
      this.hosts.conflictedWorkers = []
      if (this.hosts.selectedDatetime) {
        // if (this.hosts.selectedDatetime[1] === null) {
        //   this.hosts.selectedDatetime[1] = new Date(this.hosts.selectedDatetime[0].getTime() + 3600000)
        // }
        if (this.hosts.selectedDatetime[0] && this.hosts.selectedDatetime[1]) {
          if (this.hosts.selectedDatetime[1].getTime() - this.hosts.selectedDatetime[0].getTime() > 300000) {
            this.hosts.dateInValidated = false
          }
          if (this.hosts.selectedController && this.hosts.selectedWorker.length !== 0) {

            const endpoint = '/local/api/schedule_check/'
            const config = {
              headers: {
                'content-type': 'application/json',
                'X-CSRFTOKEN': CSRF_TOKEN
              }
            }
            const data = {
              machines: this.hosts.machineWorkers,
              start_time: this.hosts.selectedDatetime[0].toISOString(),
              end_time: this.hosts.selectedDatetime[1].toISOString()
            }
            axios
              .post(endpoint, data, config)
              .then(response => {
                if (response.status == 200) {
                  this.hosts.conflictedWorkers = response.data
                }
              })
              .catch(e => {
                this.errors.push(e)
              })
          }
        }
      }
    },
    submitUpload(event) {
      event.xhr.setRequestHeader('X-CSRFTOKEN', CSRF_TOKEN)
      console.log(event.xhr)
    },
  },
  created() {
    this.getworkloads()
    this.getMachines()
    this.columns = [
      { field: 'id', header: 'Job ID', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'workload', header: 'Workload', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'machines', header: 'Machines', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'status', header: 'Status', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'user', header: 'User', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'start_time', header: 'Start Time', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'end_time', header: 'End Time', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
    ]
  },
  watch: {
    'workload.selectedWorkload': function () {
      if (this.workload.selectedWorkload) {
        if (this.workload.selectedWorkload.name) {
          this.getVersions()
        }
      }
      else {
        this.workload.selectedWorkload = null
        this.workload.configs = {
          "jsf_repo": null,
          "registry": null,
          "commit": null,
          "filter_case": null,
          "workload_parameter": null,
        }
        this.workload.selectedVersion = null
        this.workload.versions = null
      }
    },
    'workload.selectedVersion': function () {
      if (this.workload.selectedWorkload && this.workload.selectedVersion) {
        if (this.workload.selectedWorkload.name && this.workload.selectedVersion.version) {
            this.getWorkloadConfigs()
        }
      }
      else {
        this.workload.configs = []
        this.workload.selectedVersion= null
      }
    },
    'hosts.selectedDatetime': function () {
      this.checkWorkerSchedule()
    },
    'hosts.selectedController': function () {
      this.checkWorkerSchedule()
    },
    'hosts.selectedWorker': function () {
      this.checkWorkerSchedule()
    },
    'hosts.k8sHostInstall': function () {
      if (!this.hosts.k8sHostInstall) {
        this.hosts.k8sHostInstall = true
      }
    },
    // 'hosts.k8sHostInstall': function () {
    //   if (this.hosts.k8sHostInstall) {
    //     this.hosts.k8sVMInstall = false
    //   } else {
    //     this.hosts.k8sVMInstall = true
    //   }
    // },
    // 'hosts.k8sVMInstall': function () {
    //   if (this.hosts.k8sVMInstall) {
    //     this.getVMconfigs()
    //     this.hosts.k8sHostInstall = false
    //   } else {
    //     this.hosts.k8sHostInstall = true
    //   }
    // },
  },
  directives: {
    'tooltip': Tooltip
}
}
</script>

<style lang="scss" scoped>
  ::v-deep .p-accordion .p-accordion-header .p-accordion-header-link {
    color: white !important;
    background: rgb(0, 120, 212) !important;
  }
</style>
