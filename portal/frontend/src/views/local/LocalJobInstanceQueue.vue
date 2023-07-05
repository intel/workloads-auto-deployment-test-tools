<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
<div>
  <ConfirmDialog></ConfirmDialog>
    <div>
      <DataTable
        :value='queue'
        columnResizeMode="fit"
        :paginator='false'
        :filters="filters"
        :loading="loading"
        :rows='20'
        paginatorTemplate='CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown'
        :rowsPerPageOptions='[20,50,100]'
        currentPageReportTemplate='Showing {first} to {last} of {totalRecords}'
      >
        <template #loading>
            Loading job data. Please wait.
        </template>
        <Column
          v-for="col of columns"
          :field="col.field"
          :header="col.header"
          :key="col.field"
          headerStyle="width: 1em; text-align: center; color:white; font-size:20px; background-color:grey" bodyStyle="text-align: center; color:white; background-color:grey"
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
        <template #body="slotProps" v-else-if="col.field === 'progress'">
            {{ slotProps.data.progress }}% complete
            <ProgressBar :value="slotProps.data.progress" />
          </template>
        <template #body="slotProps" v-else-if="col.field === 'status'">
            <Button
             class="p-button-success p-button-sm p-button-rounded p-button-raised"
             :label="slotProps.data.status"
             v-if="slotProps.data.status === 'FINISHED'">
            </Button>
            <Button
             class="p-button-secondary p-button-sm p-button-rounded p-button-raised"
             :label="slotProps.data.status"
             v-else-if="slotProps.data.status === 'NOT_START'">
            </Button>
            <Button
             class="p-button-warning p-button-sm p-button-rounded p-button-raised"
             :label="slotProps.data.status"
             v-else-if="slotProps.data.status === 'RUNNING'">
            </Button>
            <Button
             class="p-button-secondary p-button-sm p-button-rounded p-button-raised"
             :label="slotProps.data.status"
             v-else-if="slotProps.data.status === 'IN_QUEUE'">
            </Button>
            <Button
             class="p-button-danger p-button-sm p-button-rounded p-button-raised"
             :label="slotProps.data.status"
             v-else-if="slotProps.data.status === 'FAILURE'">
            </Button>
            <Button
             class="p-button-info p-button-sm p-button-rounded p-button-raised"
             :label="slotProps.data.status"
             v-else>
            </Button>
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
  <Toast position="top-right" />
</div>
</template>

<script>
import DataTable from 'primevue/datatable'
import Toast from 'primevue/toast'
import Column from 'primevue/column'
import ConfirmDialog from 'primevue/confirmdialog'
import ProgressBar from 'primevue/progressbar'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import axios from 'axios'

export default {
  name: 'LocalJobInstanceQueue',
  components: {
    DataTable,
    Column,
    Tag,
    ConfirmDialog,
    ProgressBar,
    Toast,
    Button
    // SpeedDial
  },
  props: {
    ip: String
  },
  data () {
    return {
      errors: [],
      filters: {},
      loading: true,
      queue: [],
      showQueue: true,
      columns: null
    }
  },
  methods: {
    getQueue () {
      const endpoint = `/local/api/job/?ip=${this.ip}`
      axios
        .get(endpoint)
        .then(response => {
          this.queue = response.data
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    refresh () {
      this.getQueue()
    }
  },
  created () {
    this.columns = [
      { field: 'id', header: 'ID', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'workload', header: 'Workload', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      // { field: 'machines', header: 'Machines', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'config', header: 'Config Version', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'config_url', header: 'Config', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      // { field: 'modified', header: 'Modified' },
      // { field: 'fail_reason', header: 'Fail Reason', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'start_time', header: 'Start Time', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'end_time', header: 'End Time', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'progress', header: 'Progress', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'status', header: 'Status', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'log', header: 'Log', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'user', header: 'Submitter', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'created', header: 'Created', style: "{'flex-grow':'1', 'flex-basis':'100px'}" }

    ]
    this.getQueue()
  }
}
</script>

<style scoped>
  .p-button-sm {
    width: 8em;
  }
  .op {
    font-style: normal;
    font-size: 0.75rem;
    letter-spacing: normal;
    line-break: auto;
    text-shadow: none;
    text-transform: none;
    white-space: normal;
    word-break: normal;
    word-spacing: normal;
    word-wrap: normal;
    text-decoration: none;
    background-color: #363636;
    color: #ffffff;
  }
  .tag {
    width: 10em;
  }
  .button {
    width: 10em;
  }
</style>
