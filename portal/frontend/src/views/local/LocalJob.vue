<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div class="font">

    <ConfirmDialog></ConfirmDialog>
    <div v-show="showJobs">
      <DataTable class="font table" responsiveLayout="scroll" :value='jobs' columnResizeMode="fit"
        :paginator='true' :filters="filters" :loading="loading" :rows='20'
        paginatorTemplate='CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown'
        :rowsPerPageOptions='[20, 50, 100]' currentPageReportTemplate='Showing {first} to {last} of {totalRecords}'>
        <template #header class="p-datatable-header">
          <div class="title-header">
            <div class="title-header-left">
              <h4 class="m-0"><b>Provision Jobs</b></h4>
            </div>
            <div class="title-header-right">
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText class="p-inputtext-sm font" v-model="filters['global']['value']" placeholder="Global Search" />
              </span>
            </div>
          </div>
        </template>
        <template #empty>
          No jobs found.
        </template>
        <template #loading>
          Loading job data. Please wait.
        </template>
        <Column v-for="col of columns" :field="col.field" :header="col.header" :key="col.field"
          :headerClass="'column-header'" bodyClass="column-body">
          <template #body="slotProps" v-if="col.field === 'config_url'">
            <Button :label="'Json'" icon="pi pi-file"
              class="p-button-raised p-button-rounded p-button-sm btn-sm" @click="showLog(slotProps.data.id)" />
          </template>
          <template #body="slotProps" v-else-if="col.field === 'log'">
            <Button :label="'Log'" icon="pi pi-file"
              class="p-button-raised p-button-rounded p-button-sm btn-sm"
              @click="showExternalLog(slotProps.data.id)" />
          </template>
          <template #body="slotProps" v-else-if="col.field === 'machines'">
            <Button v-for="machine of slotProps.data.machines.slice(0,1)" :label="machine" icon="pi pi-desktop"
              class="p-button-raised p-button-rounded btn-sm"/>
            <Button v-for="machine of slotProps.data.machines.slice(1)" :label="machine" icon="pi pi-user"
              class="p-button-raised p-button-rounded btn-sm"/>
            <!-- <Tag class="mb-1 mr-1 tag" severity="info" rounded v-for="ip of slotProps.data.machines" :value="ip"
              :key="ip"></Tag> -->
          </template>
          <!--
        <template #body="slotProps" v-else-if="col.field === 'result_link'">
          <a
            v-if="!slotProps.data.result_link"
            :href="'https://af01p-igk.devtools.intel.com/artifactory/platform_hero-igk-local/auto_provision/main_09-09-2022_264_auto-provision_d79aac4b/execution/ICX_Kafka_211.json'"
            target="_blank"
          >
          </a>
          <a
            v-else
            :href="slotProps.data.result_link"
            target="_blank"
          >
            kpi_link
          </a>
        </template>
        -->
          <template #body="slotProps" v-else-if="col.field === 'local_job_test_result'">
            <Button :label="'Result'" icon="pi pi-list"
              class="p-button-raised p-button-rounded p-button-sm btn-sm"
              @click="showLocalJobTestResult(slotProps.data.id)" />
          </template>
          <template #body="slotProps" v-else-if="col.field === 'progress'">
            {{ slotProps.data.progress }}% complete
            <ProgressBar :value="slotProps.data.progress" />
          </template>
          <template #body="slotProps" v-else-if="col.field === 'status'" @load="tt(slotProps.data.status)">
            <Tag class="mr-2" severity="success" rounded v-if="slotProps.data.status === 'SUCCESS'"
              :value="slotProps.data.status"></Tag>
            <Tag class="mr-2" severity="info" roun,,ded v-else-if="slotProps.data.status === 'TIME_PENDING'"
              :value="slotProps.data.status"></Tag>
            <Tag class="mr-2" severity="danger" rounded v-else-if="slotProps.data.status === 'FAILURE'"
              :value="slotProps.data.status"></Tag>
            <Tag class="mr-2" severity="danger" rounded v-else-if="slotProps.data.status === 'ABORTED'"
              :value="slotProps.data.status"></Tag>
            <Tag class="mr-2" severity="info" rounded v-else-if="slotProps.data.status === 'IN_QUEUE'"
              :value="slotProps.data.status"></Tag>
            <Tag class="mr-2" severity="warning" v-else rounded :value="slotProps.data.status"></Tag>
          </template>
          <template #body="slotProps" v-else-if="col.field === 'start'">
            <div v-if="!['RUNNING','TIME_PENDING' ,'IN_QUEUE', 'STARTING'].includes(slotProps.data.status) && Date.parse(slotProps.data.end_time) > new Date()">
              <Button v-tooltip="'replay job'" icon="pi pi-play" class="p-button-raised p-button-rounded p-button-sm btn-sm" @click="startJob(slotProps.data.id)"/>
            </div>
            <div v-else>
              <Button v-tooltip="'Could not start when job in one of RUNNING/TIME_PENDING/IN_QUEUE/STARTING status, or outdated'" icon="pi pi-play" class="p-button-raised p-button-rounded p-button-sm btn-sm"  disabled="true"/>
            </div>
          </template>
          <template #body="slotProps" v-else-if="col.field === 'stop'">
            <div v-if="slotProps.data.status === 'RUNNING'">
              <Button v-tooltip="'Stop job'" icon="pi pi-times" class="p-button-raised p-button-rounded p-button-sm btn-sm" @click="stopJob(slotProps.data.id)"/>
            </div>
            <div v-else>
              <Button v-tooltip="'Could not stop unless in RUNNING status'" icon="pi pi-times" class="p-button-raised p-button-rounded p-button-sm btn-sm" disabled="true"/>
            </div>
          </template>
          <template #body="slotProps" v-else-if="col.field === 'start_time'">
              <Tag :value="slotProps.data.start_time.slice(0,19).replace('T',' ')" class="column-body"></Tag>
          </template>
          <template #body="slotProps" v-else-if="col.field === 'end_time'">
              <Tag :value="slotProps.data.end_time.slice(0,19).replace('T',' ')" class="column-body"></Tag>
          </template>
          <template #body="slotProps" v-else-if="col.field === 'created'">
              <Tag :value="slotProps.data.created.slice(0,19).replace('T',' ')" class="column-body"></Tag>
          </template>
        </Column>
        <template #paginatorLeft>
          <Button type='button' icon='pi pi-refresh' class='p-button-text' @click="refresh" />
        </template>
        <template #paginatorRight>
          <Button type='button' icon='pi pi-cloud' class='p-button-text' />
        </template>
      </DataTable>
    </div>

    <Dialog :header="' ' + startMessage" :visible.sync="displayStartStatus" :style="{ width: '50%' }"
      :maximizable="false" :modal="true" v-if="jobid !== null">
        <ProgressSpinner v-if="!startMessage"/>
    </Dialog>
    <Dialog :header="' ' + stopMessage" :visible.sync="displayStopStatus" :style="{ width: '50%' }"
      :maximizable="false" :modal="true" v-if="jobid !== null">
    </Dialog>
    <Dialog :header="'Job ' + log" :visible.sync="displayLog" :style="{ width: '90%' }" :maximizable="false"
      :modal="true" v-if="log !== null">
      <LocalLogComponent :LogPath="log" />
    </Dialog>
    <Dialog :header="'Job ' + log" :visible.sync="displayExternalLog" :style="{ width: '90%' }" :maximizable="false"
      :modal="true" v-if="log !== null">
      <LocalExternalLogComponent :LogPath="log" />
    </Dialog>
    <Dialog :header="'Job ' + jobid" :visible.sync="displayLocalJobTestResult" :style="{ width: '90%' }"
      :maximizable="false" :modal="true" v-if="jobid !== null">
      <LocalJobTestResultComponent :JobId="jobid" />
    </Dialog>

  </div>
</template>

<script>
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressBar from 'primevue/progressbar'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'
import ConfirmDialog from 'primevue/confirmdialog'
import Dialog from 'primevue/dialog'
import LocalLogComponent from '@/views/local/TestLog.vue'
import LocalExternalLogComponent from '@/views/local/ExternalLog.vue'
import LocalJobTestResultComponent from '@/views/local/TestResult.vue'
import ProgressSpinner from 'primevue/progressspinner';
import Tooltip from 'primevue/tooltip';
// import Checkbox from 'primevue/checkbox'
import { CSRF_TOKEN } from '../../common/csrf_token'

import axios from 'axios'

export default {
  name: 'LocalJob',
  components: {
    ProgressBar,
    DataTable,
    ConfirmDialog,
    Column,
    Tag,
    Button,
    Dialog,
    LocalLogComponent,
    LocalExternalLogComponent,
    LocalJobTestResultComponent,
    InputText,
    ProgressSpinner,
    Tooltip,
    // Checkbox
  },
  data() {
    return {
      errors: [],
      filters: {
        "global": {
          "value":
            ""
        }
      },
      loading: true,
      jobs: [],
      selectedIds: [],
      displayExternalLog: false,
      displayLocalJobTestResult: false,
      showJobs: false,
      jobid: null,
      log: null,
      displayLog: false,
      columns: null,
      displayStartStatus: false,
      displayStopStatus: false,
      startMessage: "",
      stopMessage: "",
    }
  },
  methods: {
    startJob(id) {
      this.displayStartStatus = true
      this.jobid = id
      const endpoint = '/local/api/queue/?start_job_id=' + id
      const config = {
        header: {
          'X-CSRFTOKEN': CSRF_TOKEN
        }
      }
      axios
          .get(endpoint, config)
          .then(response => {
            this.startMessage = ""
            if (response.status == 201) {
              this.getJobs()
            }
            this.startMessage = response.data
          })
          .catch(e => {
            this.startMessage = e.response.data
            this.errors.push(e)
          })
      this.loading = false
    },
    stopJob(id) {
      this.displayStopStatus = true
      this.jobid = id
      const endpoint = '/local/api/queue/?stop_job_id=' + id
      axios
          .get(endpoint)
          .then(response => {
            this.startMessage = ""
            if (response.status == 201) {
              this.getJobs()
            }
            this.stopMessage = response.data
          })
          .catch(e => {
            this.errors.push(e)
          })
    },
    getJobs() {
      this.showJobs = true
      const endpoint = '/local/api/job/?user=true'
      const config = {
        headers: {
          'X-CSRFTOKEN': CSRF_TOKEN
        }
      }
      axios
        .get(endpoint, config)
        .then(response => {
          this.jobs = response.data
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    // getJob(job_id) {
    //   const endpoint = '/local/api/job/' + job_id + '/'
    //   axios
    //     .get(endpoint)
    //     .then(response => {
    //       console.log("one get job action start...")
    //       this.jobs.forEach (job =>{
    //         if (job.id === response.data.id) {
    //           this.jobs.splice(this.jobs.indexOf(job))
    //           this.jobs.push(response.data)
    //         }
    //       })
    //     })
    //     .catch(e => {
    //       this.errors.push(e)
    //     })
    // },
    showLog(id) {
      this.displayLog = true
      this.log = id + '_config.json'
    },
    showExternalLog(id) {
      this.displayExternalLog = true
      this.log = id.toString()
    },
    showLocalJobTestResult(id) {
      this.displayLocalJobTestResult = true
      this.jobid = id.toString()
    },
 
    refresh() {
      const endpoint = '/local/api/queue/'
      axios
        .get(endpoint)
        .then(response => {
          if (response.status === 201) {
            this.getJobs()
          }
          // let data = response.data
          // console.log(data)
          // if (data.includes("status changed")) {
          //   let dataArray = data.split("job_id::")[1].split(",")
          //   dataArray.forEach(element => {
          //     this.getJob(element)
          //   })
          // }
        })
        .catch(e => {
          this.errors.push(e)
        })
    }
  },
  created() {
    this.columns = [
      { field: 'id', header: 'ID', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'workload', header: 'Workload', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'machines', header: 'Machines', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      // { field: 'config', header: 'Config Version', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'config_url', header: 'Config', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      // { field: 'modified', header: 'Modified' },
      // { field: 'fail_reason', header: 'Fail Reason', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'start_time', header: 'Start Time', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'end_time', header: 'End Time', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      // { field: 'progress', header: 'Progress', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'status', header: 'Status', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'filter_case', header: 'Filter Case', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'local_job_test_result', header: 'KPI', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'log', header: 'Log', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'user', header: 'Submitter', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'start', header: 'Replay Job', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'stop', header: 'Stop Job', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'created', header: 'Created', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },

    ]
    this.getJobs()
  },
  mounted() {
    setInterval(() => {
      this.refresh();
    }, 3000);
  },
  directives: {
    'tooltip': Tooltip
}

}
</script>

<style lang="scss" scoped>
.p-button-sm {
  width: 8em;
}
.column-body {
  color: black !important;
  background-color: rgba(244, 248, 250, 0.15) !important;
}
</style>
