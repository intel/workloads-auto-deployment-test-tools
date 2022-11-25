<template>
<div>
  <ConfirmDialog></ConfirmDialog>
  <div class="card-header text-center">Provision Jobs</div>
    <div v-show="showJobs">
      <DataTable
        :value='jobs'
        columnResizeMode="fit"
        :paginator='true'
        :filters="filters"
        :loading="loading"
        :rows='20'
        paginatorTemplate='CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown'
        :rowsPerPageOptions='[20,50,100]'
        currentPageReportTemplate='Showing {first} to {last} of {totalRecords}'
      >
        <template #header>
          <div style="text-align: right">
            <i class="pi pi-search mt-1 mr-2"></i>
            <InputText
              v-model="filters['global']"
              placeholder="Global Search"
              class="p-inputtext-sm"
              size="50"
            />
          </div>
        </template>
        <template #empty>
            No jobs found.
        </template>
        <template #loading>
            Loading job data. Please wait.
        </template>
        <Column
          v-for="col of columns"
          :field="col.field"
          :header="col.header"
          :key="col.field"
          headerStyle="width: 1em; text-align: center; color:black; font-size:20px; background-color:#0078d4" bodyStyle="text-align: center; color:black; background-color:#80c2e926"
        >
        <template #body="slotProps" v-if="col.field === 'config_url'">
            <Button
              :label="'Json'"
              icon="pi pi-bookmark"
              class="p-button-raised p-button-rounded p-button-sm p-button-help"
              @click="showLog(slotProps.data.id)"
            />
          </template>
        <template #body="slotProps" v-else-if="col.field === 'log'">
            <Button
              :label="'Log'"
              icon="pi pi-bookmark"
              class="p-button-raised p-button-rounded p-button-sm p-button-help"
              @click="showExternalLog(slotProps.data.id)"
            />
          </template>
        <template #body="slotProps" v-else-if="col.field === 'machines'">
            <Tag class="mb-1 mr-1 tag" severity="info" rounded
              v-for="ip of slotProps.data.machines"
                :value="ip"
                :key="ip"
            ></Tag>
          </template>
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
        <template #body="slotProps" v-else-if="col.field === 'progress'">
            {{ slotProps.data.progress }}% complete
            <ProgressBar :value="slotProps.data.progress" />
          </template>
        <template #body="slotProps" v-else-if="col.field === 'status'">
          <Tag
            class="mr-2"
            severity="success"
            rounded
            v-if="slotProps.data.status === 'FINISHED'"
            :value="slotProps.data.status"></Tag>
          <Tag
            class="mr-2"
            severity="info"
            rounded
            v-else-if="slotProps.data.status === 'NOT_START'"
            :value="slotProps.data.status"></Tag>
          <Tag
            class="mr-2"
            severity="warning"
            rounded
            v-else-if="slotProps.data.status === 'RUNNING'"
            :value="slotProps.data.status"></Tag>
          <Tag
            class="mr-2"
            severity="warning"
            rounded
            v-else-if="slotProps.data.status === 'JENKINS_RUNNING'"
            :value="slotProps.data.status"></Tag>
          <Tag
            class="mr-2"
            severity="info"
            rounded
            v-else-if="slotProps.data.status === 'IN_QUEUE'"
            :value="slotProps.data.status"></Tag>
          <Tag
            class="mr-2"
            severity="danger"
            v-else
            rounded
            :value="slotProps.data.status"></Tag>
          </template>
        </Column>
        <template #paginatorLeft>
          <Button
            type='button'
            icon='pi pi-refresh'
            class='p-button-text'
            @click="refresh"
          />
        </template>
        <template #paginatorRight>
          <Button type='button' icon='pi pi-cloud' class='p-button-text' />
        </template>
      </DataTable>
    </div>
  <Dialog
    :header="'instance ' + log"
    :visible.sync="displayLog"
    :style="{width: '90%'}"
    :maximizable="false"
    :modal="true"
    v-if="log !== null"
  >
    <LocalLogComponent
      :LogPath="log"
    />
  </Dialog>
  <Dialog
    :header="'instance ' + log"
    :visible.sync="displayExternalLog"
    :style="{width: '90%'}"
    :maximizable="false"
    :modal="true"
    v-if="log !== null"
  >
    <LocalExternalLogComponent
      :LogPath="log"
    />
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

// import Checkbox from 'primevue/checkbox'
// import { CSRF_TOKEN } from '../../common/csrf_token'

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
    InputText
    // Checkbox
  },
  data () {
    return {
      errors: [],
      filters: {},
      loading: true,
      jobs: [],
      selectedIds: [],
      displayExternalLog: false,
      showJobs: false,
      jobid: null,
      log: null,
      displayLog: false,
      columns: null
    }
  },
  methods: {
    getJobs () {
      this.showJobs = true
      const endpoint = '/local/api/job/?user=true'
      axios
        .get(endpoint)
        .then(response => {
          this.jobs = response.data
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    showJob (jobid) {
      this.showJobs = true
      this.getJobs()
    },
    showLog (id) {
      this.displayLog = true
      this.log = id + '_config.json'
    },
    showExternalLog (id) {
      this.displayExternalLog = true
      this.log = id.toString()
    },
    refresh () {
      this.getJobs()
    }
  },
  created () {
    this.columns = [
      { field: 'id', header: 'ID', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'workload', header: 'Workload', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'machines', header: 'Machines', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'config', header: 'Config Version', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'config_url', header: 'Config', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      // { field: 'modified', header: 'Modified' },
      // { field: 'fail_reason', header: 'Fail Reason', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'start_time', header: 'Start Time', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'end_time', header: 'End Time', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'progress', header: 'Progress', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'status', header: 'Status', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'filter_case', header: 'filter_case', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'result_link', header: 'KPI', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'log', header: 'Log', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'user', header: 'Submitter', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'created', header: 'Created', style: "{'flex-grow':'1', 'flex-basis':'100px'}" }

    ]
    this.getJobs()
  }
}
</script>

<style scoped>
  .p-button-sm {
    width: 8em;
  }
</style>
