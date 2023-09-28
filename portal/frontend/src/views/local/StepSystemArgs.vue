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
        <span>System Args(Optional)</span>
      </div>
      <div>
        <el-form label-position="right" label-width="80px" :model="formData">
          <div class="p-formgroup-inline">
            <div class="p-field p-col-6">
              <h5>System Deploy Args</h5>
              <el-switch
              v-model="system_deploy_args"
              active-color="#13ce66"
              inactive-color="#ff4949">
              </el-switch>
            </div>
          </div>
          <div class="p-formgroup-inline" v-show="system_deploy_args">
            <div class="p-field p-col-2">
              <h5>Kernel Update</h5>
              <el-switch
              v-model="kernel_update"
              active-color="#13ce66"
              inactive-color="#ff4949">
              </el-switch>
            </div>
            <div class="p-field p-col-2">
              <h5>Kernel Args Update</h5>
              <el-switch
              v-model="kernel_args_update"
              active-color="#13ce66"
              inactive-color="#ff4949">
              </el-switch>
            </div>
          </div>
          <div v-show="os_update_show">
            <div class="p-field p-col-3">
                <h5>OS</h5>
                <Dropdown
                v-model="formData.selectedOS"
                :options="formData.OS"
                optionLabel="value"
                placeholder="OS to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
          </div>
          <div v-show="kernel_update_show">
            <div class="p-field p-col-3">
                <h5>Kernel Version</h5>
                <Dropdown
                v-model="formData.selectedKernelVersion"
                :options="formData.KernelVersion"
                optionLabel="value"
                placeholder="Kernel version to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
          </div>
          <div v-show="kernel_args_update_show">
            <div class="p-field p-col-3">
                <h5>Kernel Args</h5>
                <Dropdown
                v-model="formData.selectedKernelArgs"
                :options="formData.KernelArgs"
                optionLabel="value"
                placeholder="Kernel args to choose..."
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
import MultiSelect from 'primevue/multiselect'
export default {
  components: {
    Dropdown,
    MultiSelect
  },
  data () {
    return {
      system_deploy_args: this.formData.system_deploy_args,
      os_update: this.formData.os_update,
      os_update_show: this.formData.system_deploy_args && this.formData.os_update,
      kernel_update: this.formData.kernel_update,
      kernel_update_show: this.formData.system_deploy_args && this.formData.kernel_update,
      kernel_args_update: this.formData.kernel_args_update,
      kernel_args_update_show: this.formData.system_deploy_args && this.formData.kernel_args_update,
      selectedOS: null,
      selectedKernelVersion: null,
      selectedKernelArgs: null,
      height: this.formData.system_deploy_args ? 700 : 400
    }
  },
  props: {
    formData: Object
  },
  methods: {
    update_show () {
      this.os_update_show = this.system_deploy_args && this.os_update
      this.kernel_update_show = this.system_deploy_args && this.kernel_update
      this.kernel_args_update_show = this.system_deploy_args && this.kernel_args_update
      this.formData.system_deploy_args = this.system_deploy_args
      this.formData.os_update = this.os_update
      this.formData.kernel_update = this.kernel_update
      this.formData.kernel_args_update = this.kernel_args_update
      if (this.system_deploy_args === true) {
        this.height = 700
      } else {
        this.height = 400
      }
    }
  },
  watch: {
    system_deploy_args: function () {
      this.update_show()
    },
    os_update: function () {
      this.update_show()
    },
    kernel_update: function () {
      this.update_show()
    },
    kernel_args_update: function () {
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
