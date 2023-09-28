<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div class="font main-content">
    <ConfirmDialog class="font"></ConfirmDialog>
    <div v-show="showConfigs" class="font">
      <DataTable :value='configWorkloads' :paginator='true' :autoLayout='true'
        responsiveLayout="scroll" :resizableColumns='true' columnResizeMode='expand' :filters="filters" :loading="loading"
        :selection.sync="selectedIds" :rows='50'
        paginatorTemplate='CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown'
        :rowsPerPageOptions='[20, 50, 100]' currentPageReportTemplate='Showing {first} to {last} of {totalRecords}'>
        <template #header class="p-datatable-header">
          <div class="title-header">
            <div class="title-header-left">
              <h4 class="m-0"><b>Workloads Config</b></h4>
            </div>
            <div class="title-header-right">
              <span class="p-input-icon-left">
                  <i class="pi pi-search" />
                  <InputText class="p-inputtext-sm font" v-model="filters['global']['value']" placeholder="Global Search" />
                  <Button type="button" icon="pi pi-refresh" class="p-button-text font" @click="refresh" />
              </span>
            </div>
          </div>
        </template>
        <template #empty>
          <div class="emptyOrLoading">
            No jobs found.
          </div>
        </template>
        <template #loading>
          <div class="emptyOrLoading">
          Loading job data. Please wait.
          </div>
        </template>
        <Column v-for="col of columns" :field="col.field" :header="col.header" :key="col.field" headerClass="column-header" bodyClass="column-body">
          <template #body="slotProps" v-if="col.field === 'status'">
            <Button class="p-button-success p-button-sm" :label="slotProps.data.status"
              v-if="slotProps.data.status === 'FINISHED'">
            </Button>
            <Button class="p-button-secondary p-button-sm" :label="slotProps.data.status"
              v-else-if="slotProps.data.status === 'NOT_START'">
            </Button>
            <Button class="p-button-warning p-button-sm" :label="slotProps.data.status"
              v-else-if="slotProps.data.status === 'RUNNING'">
            </Button>
            <Button class="p-button-danger p-button-sm" :label="slotProps.data.status"
              v-else-if="slotProps.data.status === 'FAILURE'">
            </Button>
            <Button class="p-button-info p-button-sm" :label="slotProps.data.status" v-else>
            </Button>
          </template>
          <template #body="slotProps" v-else-if="col.field === 'jenkins_id'">
            <a :href="'http://172.17.120.39:8080/job/ServicesFramework/job/post-silicon-validation/job/cloud_full_validation/' + slotProps.data.jenkins_id"
              target="_blank">
              {{slotProps.data.jenkins_id}}
            </a>
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
  </div>
</template>

<script>
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import ConfirmDialog from 'primevue/confirmdialog'
// import Checkbox from 'primevue/checkbox'
// import { CSRF_TOKEN } from '../../common/csrf_token'

import axios from 'axios'

export default {
  name: 'LocalJob',
  components: {
    DataTable,
    ConfirmDialog,
    Column,
    Button,
    InputText
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
      configs: [],
      workloads: [],
      configWorkloads: [],
      componentparams: [],
      selectedIds: [],
      showConfigs: false,
      columns: null
    }
  },
  methods: {
    getConfigs() {
      this.showConfigs = true
      const endpoint = '/local/api/workload_system_config/'
      axios
        .get(endpoint)
        .then(response => {
          this.configs = response.data
          this.configWorkloads = []
          for (var config of this.configs) {
            for (var workload of this.workloads) {
              if (config.workload_id === workload.id) {
                for (var param of this.componentparams) {
                  if (config.component_param_id === param.id) {
                    console.log(param.param)
                    this.configWorkloads.push({ workload_name: workload.name, component_param: param.param, version: config.version, value: config.value, created: config.created, modified: config.modified })
                  }
                }
              }
            }
            // for (var param of this.componentparams) {
            //   console.log(param.param)
            //   if (config.component_param_id === param.component_id) {
            //     this.configWorkloads.push({ workload_name: workload.name, component_param: param.param, version: config.version, value: config.value, created: config.created, modified: config.modified })
            //   }
            // }
          }
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    getWorkloads() {
      const endpoint = '/local/api/workload/'
      axios
        .get(endpoint)
        .then(response => {
          this.workloads = response.data
          this.getComponentParams()
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    getComponentParams() {
      const endpoint = '/local/api/component_param/'
      axios
        .get(endpoint)
        .then(response => {
          this.componentparams = response.data
          this.getConfigs()
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    refresh() {
      this.getConfigs()
    }
  },
  created() {
    this.columns = [
      // { field: 'id', header: 'ID', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'workload_name', header: 'workload_name', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'component_param', header: 'component_param', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'version', header: 'version', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'value', header: 'value', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      // { field: 'modified', header: 'Modified' },
      // { field: 'fail_reason', header: 'Fail Reason', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'created', header: 'created', style: "{'flex-grow':'1', 'flex-basis':'100px'}" },
      { field: 'modified', header: 'modified', style: "{'flex-grow':'1', 'flex-basis':'100px'}" }

    ]
    this.getWorkloads()
  }
}
</script>

<style scoped>
.p-button-sm {
  width: 8em;
}
</style>
