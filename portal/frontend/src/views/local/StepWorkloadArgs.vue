<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
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
          <div v-if="formData.selectedWorkloadName.name === 'Smart-Sport-Analyzer'" class="p-field p-col-6">
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
              <el-button slot="trigger" size="medium" type="primary">Select</el-button>
              <div slot="tip" class="el-upload__tip">Only MP4 file, number less than 5, single size less than 1GB </div>
              <div slot="tip" class="el-upload-list__item-name">{{fileName}}</div>
              <el-button style="margin-left: 10px;" size="medium" type="success" @click="submitUpload">Upload</el-button>
              <el-dialog title="Upload Process" :visible="dialog" append-to-body
                :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false">
                <el-progress :percentage="progress"></el-progress>
                  <p style="text-align: center; margin: 10px 0;">
                    Uploaded: {{ loaded }}, Sum: {{total}}
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
    async handleChange(uploadFile, uploadFiles) {
      function fileReader(blob) {
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.readAsBinaryString(blob);
          reader.onload = (ret) => {
            const res = reader.result.split('').map((o) => o.charCodeAt().toString(16).padStart(2, '0'));
            resolve(res.join(' ').toUpperCase());
          },
          reader.onerror = (err) => {
            reject(err);
          };
        });
      }
      async function videoTypeIsMP4(file) {
        return await fileReader(file.slice(0, 8)) == "00 00 00 20 66 74 79 70";  // MP4 header
      }
      var file_is_valid = true
      const file_size = uploadFile.size / 1024 / 1024
      if (file_size <= 1 || file_size >= 1024) { // 1MB <= size <= 1024MB 
        this.$message.error('The size of file is too small or too big!')
        file_is_valid = false
      }
      await videoTypeIsMP4(uploadFile.raw).then(flag => {
        if (!flag) {
          this.$message.error('This type of file is not MP4!')
          file_is_valid = false
        }
      })
      if (!file_is_valid) {
        this.$refs.upload.handleRemove(uploadFile)
      } 
      this.fileList = uploadFiles 
    },
    handleRemove(uploadFile, uploadFiles) {
      this.fileList = uploadFiles;
    },
    handleExceed(uploadFile, uploadFiles) {
      this.$message.warning('Number limited to 5');
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
          this.$message.success('Upload Successful')
          this.$refs.upload.clearFiles()
          this.progress = this.loaded = this.total = 0
          this.dialog = false
        })
        .catch(e => {
          this.$message.error('Upload Error')
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
