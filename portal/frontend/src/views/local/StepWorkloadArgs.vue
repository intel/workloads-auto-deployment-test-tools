<template>
  <div align="center">
  <div class="p-field p-col-9 p-md-9 text-align-left">
    <el-card class="box-card" v-bind:style="{'height': height +'px'}">
      <div slot="header" class="clearfix">
        <span>Workload Args</span>
      </div>
      <div>
        <el-form label-position="right" label-width="80px" :model="formData">
          <!-- <div class="p-field p-col-3">
            <h5>Deploy Workload Args</h5>
            <el-switch
            v-model="deploy_workload_args"
            active-color="#13ce66"
            inactive-color="#ff4949">
            </el-switch>
          </div> -->
          <div class="p-formgroup-inline"  v-show="deploy_workload_args">
            <div class="p-field p-col-3">
              <h5>Jenkins Args</h5>
              <el-switch
              v-model="jenkins_args"
              active-color="#13ce66"
              inactive-color="#ff4949">
              </el-switch>
            </div>
            <!-- <div class="p-field p-col-3">
              <h5>Workload Package Args</h5>
              <el-switch
              v-model="workload_package_args"
              active-color="#13ce66"
              inactive-color="#ff4949">
              </el-switch>
            </div> -->
          </div>
          <div v-show="jenkins_args_show">
            <div class="p-formgroup-inline">
              <div class="p-field p-col-3">
                <h5>Workload Name</h5>
                <Dropdown
                v-model="formData.selectedWorkloadName"
                :options="formData.WorkloadName"
                optionLabel="name"
                placeholder="Workload name to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>JSF Repo</h5>
                <InputText
                type="text"
                v-model="formData.selectedJSFRepo"
               />
              </div>
            </div>
            <div class="p-formgroup-inline">
              <div class="p-field p-col-3">
                <h5>Commit</h5>
                <InputText
                type="text"
                v-model="formData.selectedCommit"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Registry</h5>
                <Dropdown
                v-model="formData.selectedRegistry"
                :options="formData.Registry"
                optionLabel="value"
                placeholder="Registry to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
            </div>
            <div class="p-formgroup-inline">
              <div class="p-field p-col-3">
                <h5>Case Filter</h5>
                <InputText
                type="text"
                v-model="formData.selectedCaseFilter"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Workload Parameters</h5>
                <InputText
                type="text"
                v-model="formData.selectedWorkloadParameter"
               />
              </div>
            </div>
          </div>
          <div v-if="formData.selectedWorkloadName.name === '3DHuman-Pose-Estimation'" class="p-field p-col-6">
            <h5>Upload video files</h5>
            <el-upload
            class="upload-demo"
            ref="upload"
            action=""
            accept=".mp4"
            :multiple="true"
            :limit="5"
            :file-list="fileList"
            :auto-upload="false"
            :on-change="handleChange"
            :on-remove="handleRemove"
            :on-exceed="handleExceed"
            :on-progress="handleProgress">
              <el-button slot="trigger" size="medium" type="primary">选取文件</el-button>
              <div slot="tip" class="el-upload__tip">只能上传mp4文件，数量不能超过5个，且每个大小不超过1GB </div>
              <div slot="tip" class="el-upload-list__item-name">{{fileName}}</div>
              <el-button style="margin-left: 10px;" size="medium" type="success" @click="submitUpload">上传</el-button>
              <el-dialog title="上传进度" :visible="dialog" append-to-body
                :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false">
                <el-progress :percentage="progress"></el-progress>
                  <p style="text-align: center; margin: 10px 0;">
                    已上传大小：{{ loaded }}，总大小： {{total}} 
                  </p>
              </el-dialog>
            </el-upload> 
          </div>
          <div v-show="workload_package_args_show">
            <div class="p-formgroup-inline">
              <div class="p-field p-col-3">
                <h5>Deploy Mode</h5>
                <Dropdown
                v-model="formData.selectedDeployMode"
                :options="formData.DeployMode"
                optionLabel="value"
                placeholder="Deploy mode to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Task Path</h5>
                <InputText
                type="text"
                v-model="formData.selectedTaskPath"
               />
              </div>
            </div>
            <div class="p-formgroup-inline">
              <div class="p-field p-col-3">
                <h5>PSF Repo</h5>
                <InputText
                type="text"
                v-model="formData.selectedPSFRepo"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Args</h5>
                <MultiSelect
                v-model="formData.selectedWorkloadArgs"
                :options="formData.WorkloadArgs"
                optionLabel="value"
                placeholder="Args to provision..."
                display="chip"
                />
              </div>
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
import MultiSelect from 'primevue/multiselect'
import InputText from 'primevue/inputtext'
import { CSRF_TOKEN } from '../../common/csrf_token'
import axios from 'axios'
export default {
  components: {
    Dropdown,
    MultiSelect,
    InputText
  },
  data () {
    return {
      deploy_workload_args: this.formData.deploy_workload_args,
      jenkins_args: this.formData.jenkins_args,
      jenkins_args_show: this.formData.deploy_workload_args && this.formData.jenkins_args,
      workload_package_args: this.formData.workload_package_args,
      workload_package_args_show: this.formData.deploy_workload_args && this.formData.workload_package_args,
      selectedWorkloadName: null,
      selectedJSFRepo: null,
      selectedCommit: null,
      selectedRegistry: null,
      selectedCaseFilter: null,
      selectedWorkloadParameter: null,
      selectedDeployMode: null,
      selectedTaskPath: null,
      selectedPSFRepo: null,
      selectedWorkloadArgs: null,
      height: this.formData.deploy_workload_args ? 700 : 400,
      fileList: [],
      dialog: false,
      loaded: 0,
      total: 0,
      progress: 0
    }
  },
  props: {
    formData: Object
  },
  methods: {
    update_show () {
      this.jenkins_args_show = this.deploy_workload_args && this.jenkins_args
      this.workload_package_args_show = this.deploy_workload_args && this.workload_package_args
      this.formData.deploy_workload_args = this.deploy_workload_args
      this.formData.jenkins_args = this.jenkins_args
      this.formData.workload_package_args = this.workload_package_args
      if (this.deploy_workload_args === true) {
        this.height = 700
      } else {
        this.height = 400
      }
    },
    handleChange(file, fileList) {
      const isLt100M = fileList.every(file => file.size / 1024 / 1024  < 1024);
      if (!isLt100M) {
          this.$message.error('请检查, 上传单个文件大小不能超过1024MB!');
          return false
      }
      this.fileList = fileList
    },
    handleRemove(files, fileList) {
      this.fileList = fileList;
    },
    handleExceed(files, fileList) {
      this.$message.warning('当前限制选择 5 个文件');
    },
    submitUpload() {
      const endpoint = '/local/api/upload_video_check/'
      let formData = new FormData();
      this.fileList.forEach((file) => {
        formData.append('files', file.raw)
      })
      this.dialog = true
      this.progress = this.loaded = this.total = 0
      const config = {
        headers: {
          'content-type': 'multipart/form-data',
          'X-CSRFTOKEN': CSRF_TOKEN
        },
        onUploadProgress: pe => {
          this.progress = Number.parseInt((pe.loaded / pe.total) * 100)
          this.loaded = pe.loaded
          this.total = pe.total
        }
      }
      axios
        .post(endpoint, formData, config)
        .then(response => {
          this.$message.success('上传成功')
          this.$refs.upload.clearFiles()
          this.progress = this.loaded = this.total = 0
          this.dialog = false
        })
        .catch(e => {
          this.$message.error('上传失败')
          this.$refs.upload.clearFiles()
          this.progress = this.loaded = this.total = 0
          this.dialog = false
        })
    }
  },
  watch: {
    deploy_workload_args: function () {
      this.update_show()
    },
    jenkins_args: function () {
      this.workload_package_args = !this.jenkins_args
      this.update_show()
    },
    workload_package_args: function () {
      this.jenkins_args = !this.workload_package_args
      this.update_show()
    }
  }
}
</script>

<style scoped>
.text-align-left {
  text-align: left;
}
</style>
