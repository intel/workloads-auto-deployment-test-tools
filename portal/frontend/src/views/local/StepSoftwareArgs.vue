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
        <span>Software Args</span>
      </div>
      <div>
        <el-form label-position="right" label-width="80px" :model="formData">
          <div class="p-formgroup-inline">
            <div class="p-field p-col-6">
              <h5>Software Package Args(Optional)</h5>
              <el-switch
              v-model="software_package_args"
              active-color="#13ce66"
              inactive-color="#ff4949"
              :disabled="this.switchEnable">
              </el-switch>
            </div>
          </div>
          <div class="p-formgroup-inline" v-show="software_package_args">
            <div class="p-field p-col-2">
              <h5>DPDK</h5>
              <el-switch
              v-model="DPDK"
              active-color="#13ce66"
              inactive-color="#ff4949"
              >
              </el-switch>
            </div>
          </div>
          <div v-show="DPDK_show">
            <div class="p-field p-col-6">
                <h5>DPDK Args</h5>
                <InputText
                type="text"
                v-model="formData.selectedDPDKArgs"
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
import InputText from 'primevue/inputtext'
export default {
  components: {
    InputText
  },
  data () {
    return {
      switchEnable: true,
      software_package_args: this.formData.software_package_args,
      DPDK: this.formData.DPDK,
      DPDK_show: this.formData.software_package_args && this.formData.DPDK,
      selectedDPDKArgs: null,
      height: this.formData.software_package_args ? 700 : 400
    }
  },
  props: {
    formData: Object
  },
  methods: {
    update_show () {
      this.DPDK_show = this.software_package_args && this.DPDK
      this.formData.software_package_args = this.software_package_args
      this.formData.DPDK = this.DPDK
      if (this.software_package_args === true) {
        this.height = 700
      } else {
        this.height = 400
      }
    }
  },
  watch: {
    software_package_args: function () {
      this.update_show()
    },
    DPDK: function () {
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
