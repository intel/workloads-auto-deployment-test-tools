<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
<div>
    <DataTable 
        :value="test_result" 
        class="p-datatable-sm"
        :resizableColumns="true" 
        :paginator="true"
        :rows="10"
        :rowHover="true"
        :loading="loading"
        :rowsPerPageOptions="[10, 15, 20]"
        :globalFilterFields="['test_result', 'test_time']"
        responsiveLayout="scroll"
    >
        <template #header>
          <div style="text-align:center; font-size:large">
            Test Result
          </div>
        </template>
        <template #empty>
          <div style="text-align:center;">
            No test result data found.
          </div>
        </template>
        <template #loading> 
          <div style="text-align:center">
            Loading test result data. Please wait.
          </div>
        </template>
        <Column field="test_case" header="Case"></Column>
        <Column field="test_result" header="Result">
          <template #body="{ data }">
            <span :class="data.test_result">{{ data.test_result }}</span>
          </template>
        </Column>
        <Column field="kpi_key" header="KPI NAME">
          <template #body="{ data }">
            <span >{{ data.kpi_key }}</span>
          </template>
        </Column>
        <Column field="kpi_value" header="KPI Value">
          <template #body="{ data }">
            <span>{{ data.kpi_value }}</span>
          </template>
        </Column>
        <Column field="test_time" header="Duration">
          <template #body="{ data }">
            <span>{{ data.test_time }}</span>
          </template>
        </Column>
    </DataTable>
</div>
</template>

<script>
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ColumnGroup from 'primevue/columngroup'
import Row from 'primevue/row'
import axios from 'axios'
export default {
  name: 'LocalJobTestResultComponent',
  components: {
    DataTable,
    Column,
    ColumnGroup,
    Row
  },
  props: {
    JobId: String
  },
  data () {
    return {
      errors: [],
      polling: null,
      result: null,
      test_result: null,
      loading: true,
      test_results: ['PASSED', 'FAILED'],
    }
  },
  methods: {
    getTestResult () {
      const endpoint = `/local/api/test_result/?job_id=${this.JobId}`
      const config = { 'Cache-Control': 'no-store' }
      axios
        .get(endpoint, config)
        .then(response => {
          console.log('=========== here is get test_result of ==========')
          console.log('<<<<<<<<<<<<< ' + this.JobId + ' >>>>>>>>>>>>>>')
          response.data.forEach(element => {
            for (var key in element) {
              if (element[key] === null || element[key] === '') {
                element[key] = '-'
              }
            }
            if (element.test_result == 'PASS') {
                element.test_result = 'PASSED'
            }
          })
          console.log(response.data)
          this.test_result = response.data
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
          if (e.response.status === 404) {
            this.test_result = 'The test run result is not created yet. Please wait for the job to start or rebuild it.'
          } else {
            this.test_result = e
          }
        })
    },
    pollData () {
      this.polling = setInterval(() => {
        this.getTestResult()
      }, 100000)
    }
  },
  created () {
    this.getTestResult()
    this.pollData()
  },
  beforeDestroy () {
    clearInterval(this.polling)
  }
}
</script>
<style scoped>
.PASSED {
  border-radius: 2px;
  padding: .25em .5rem;
  text-transform: uppercase;
  font-weight: 700;
  font-size: 12px;
  letter-spacing: .3px;
  background-color: #C8E6C9;
  color: #256029;
}
.FAILED {
  border-radius: 2px;
  padding: .25em .5rem;
  text-transform: uppercase;
  font-weight: 700;
  font-size: 12px;
  letter-spacing: .3px;
  background-color: #FFCDD2;
  color: #C63737; 
}
</style>