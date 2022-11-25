<template>
  <div align="center">
  <div class="p-field p-col-9 p-md-9 text-align-left">
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>Deploy Host</span>
      </div>
      <div>
        <el-form label-position="right" label-width="80px" :model="formData">
          <div class="p-formgroup-inline">
            <div class="p-field p-col-3">
              <h5>Controller</h5>
              <MultiSelect
              v-model="selectedController"
              :options="MachineControllers"
              optionLabel="show_name"
              placeholder="Controller to provision..."
              :filter="true"
              />
            </div>
            <div class="p-field p-col-3">
              <h5>Worker</h5>
              <MultiSelect
              v-model="selectedWorker"
              :options="MachineWorkers"
              optionLabel="show_name"
              placeholder="Workers to provision..."
              :filter="true"
              />
            </div>
            <div class="p-field p-col-4">
              <h5>Select Using Time Range</h5>
              <el-date-picker
                v-model="selectedDatetime"
                type="datetimerange"
                size="large"
                start-placeholder="Start Date"
                end-placeholder="End Date"
               :default-time="[startTime, endTime]"
               :picker-options="{ disabledDate: (date) => disabledEndDate(date) }">
              </el-date-picker>
            </div>
            <div>
              <h5>Worker Check</h5>
              <div v-show="this.formData.checkGreen">
                <el-button type="success" icon="el-icon-check" circle></el-button>
              </div>
              <div v-show="this.formData.checkRed">
                <el-button type="danger" icon="el-icon-close" circle></el-button>
              </div>
            </div>
          </div>
          <div class="p-field p-col-9">
            <h5>Workers in Use/Queue</h5>
            <el-table
            :data="this.formData.tableData"
            style="width: 100%">
              <el-table-column
                prop="workload"
                label="Workload">
              </el-table-column>
              <el-table-column
                prop="machines"
                label="Machines">
              </el-table-column>
              <el-table-column
                prop="status"
                label="Status">
              </el-table-column>
              <el-table-column
                prop="progress"
                label="Progress">
              </el-table-column>
              <el-table-column
                prop="user"
                label="User">
              </el-table-column>
              <el-table-column
                prop="start_time"
                label="Start Time">
              </el-table-column>
              <el-table-column
                prop="end_time"
                label="End Time">
              </el-table-column>
            </el-table>
          </div>
        </el-form>
      </div>
    </el-card>
  </div>
  </div>
</template>
<script>
import MultiSelect from 'primevue/multiselect'
import axios from 'axios'
import { CSRF_TOKEN } from '../../common/csrf_token'
export default {
  components: {
    MultiSelect
  },
  data () {
    return {
      MachineControllers: this.formData.MachineControllers,
      selectedController: this.formData.selectedController,
      MachineWorkers: this.formData.MachineWorkers,
      selectedWorker: this.formData.selectedWorker,
      selectedDatetime: this.formData.selectedDatetime,
      // selectedDatetime: [new Date(Date.UTC((new Date()).getFullYear(), (new Date()).getMonth(), (new Date()).getDate(), (new Date()).getHours(), (new Date()).getMinutes(), (new Date()).getSeconds())).toISOString().slice(0, 19), new Date(Date.UTC((new Date()).getFullYear(), (new Date()).getMonth(), (new Date()).getDate(), (new Date()).getHours(), (new Date()).getMinutes(), (new Date()).getSeconds())).toISOString().slice(0, 19)],
      startTime: new Date(Date.UTC((new Date()).getFullYear(), (new Date()).getMonth(), (new Date()).getDate(), (new Date()).getHours(), (new Date()).getMinutes() , (new Date()).getSeconds())).toISOString().slice(11, 19),
      endTime: new Date(Date.UTC((new Date()).getFullYear(), (new Date()).getMonth(), (new Date()).getDate(), (new Date()).getHours(), (new Date()).getMinutes() + 5, (new Date()).getSeconds())).toISOString().slice(11, 19),
      tableData: null,
      checkGreen: false,
      checkRed: false
    }
  },
  props: {
    formData: Object
  },
  methods: {
    getWorkersQueue (worker) {
      const endpoint = '/local/api/job/?ip=' + worker
      axios
        .get(endpoint)
        .then(response => {
          this.formData.tableData = []
          for (var res of response.data) {
            this.formData.tableData.push({ workload: res.workload, machines: res.machines, status: res.status, progress: res.progress, user: res.user, start_time: res.start_time, end_time: res.end_time })
          }
        })
        .catch(e => {
          this.errors.push(e)
        })
    },
    disabledEndDate (date) {
      var tdate = new Date()
      var previousDate = tdate.setDate(tdate.getDate() - 1)
      return date.getTime() < previousDate
    },
    checkWorkerSchedule (workers, timeRange) {
      const endpoint = '/local/api/schedule_check/'
      const config = {
        headers: {
          'content-type': 'application/json',
          'X-CSRFTOKEN': CSRF_TOKEN
        }
      }
      const data = {
        machines: workers,
        start_time: timeRange[0],
        end_time: timeRange[1]
      }
      axios
        .post(endpoint, data, config)
        .then(response => {
          this.formData.checkGreen = true
          this.formData.checkRed = false
        })
        .catch(e => {
          this.formData.checkGreen = false
          this.formData.checkRed = true
        })
    }
  },
  watch: {
    selectedDatetime: function () {
      this.formData.selectedDatetime = []
      if (this.selectedDatetime === null) {
        this.checkGreen = false
        this.formData.checkGreen = false
        this.checkRed = false
        this.formData.checkRed = false
        return
      }
      var timezone = String(Math.abs(this.selectedDatetime[0].getTimezoneOffset() / 60))
      if (timezone.length < 2) {
        timezone = '0' + timezone
      }
      timezone = timezone + ':00'
      this.formData.selectedDatetime.push(String(this.selectedDatetime[0].getFullYear()) + '-' +
      String(this.selectedDatetime[0].getMonth() + 1) + '-' +
      String(this.selectedDatetime[0].getDate()) + ' ' +
      String(this.selectedDatetime[0].getHours()) + ':' +
      String(this.selectedDatetime[0].getMinutes()) + ':' +
      String(this.selectedDatetime[0].getSeconds()) + '+' + timezone)
      this.formData.selectedDatetime.push(String(this.selectedDatetime[1].getFullYear()) + '-' +
      String(this.selectedDatetime[1].getMonth() + 1) + '-' +
      String(this.selectedDatetime[1].getDate()) + ' ' +
      String(this.selectedDatetime[1].getHours()) + ':' +
      String(this.selectedDatetime[1].getMinutes()) + ':' +
      String(this.selectedDatetime[1].getSeconds()) + '+' + timezone)
      if (this.selectedWorker.length !== 0) {
        var workers = []
        for (var worker of this.selectedWorker) {
          workers.push(worker.ip)
        }
        this.checkWorkerSchedule(workers, this.formData.selectedDatetime)
      }
    },
    selectedController: function () {
      this.formData.selectedController = this.selectedController
    },
    selectedWorker: function () {
      this.formData.selectedWorker = this.selectedWorker
      if (this.selectedWorker.length !== 0) {
        var workers = []
        for (var worker of this.selectedWorker) {
          workers.push(worker.ip)
        }
        this.getWorkersQueue(workers.join(','))
        if (this.formData.selectedDatetime !== null) {
          this.checkWorkerSchedule(workers, this.formData.selectedDatetime)
        }
      } else {
        this.formData.tableData = null
        this.formData.checkGreen = false
        this.formData.checkRed = false
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
