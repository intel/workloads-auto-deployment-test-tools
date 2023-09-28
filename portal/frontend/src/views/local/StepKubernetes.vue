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
        <span>Kubernetes</span>
      </div>
      <div>
        <el-form label-position="right" label-width="80px" :model="formData">
          <div class="p-field p-col-3">
            <h5>Reset Kubernetes</h5>
            <el-switch
            v-model="formData.deploy_kubernetes_v2"
            active-color="#13ce66"
            inactive-color="#a9a9a9">
            </el-switch>
          </div>
          <div class="p-field p-col-3" v-show="formData.deploy_kubernetes">
            <h5>Kubernetes Install Method</h5>
            <Dropdown
            v-model="selectedKubernetesInstallMethod"
            :options="formData.KubernetesInstallMethod"
            optionLabel="value"
            placeholder="Kubernetes install method to choose..."
            :filter="true"
            :showClear="true"
            />
          </div>
          <div v-show="formData.deploy_kubernetes">
            <div class="p-formgroup-inline">
              <div class="p-field p-col-3">
                <h5>Kubernetes Version</h5>
                <Dropdown
                v-model="formData.selectedKubernetesVersion"
                :options="formData.KubernetesVersion"
                optionLabel="value"
                placeholder="Kubernetes version to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Kubernetes Network Plugin</h5>
                <Dropdown
                v-model="formData.selectedKubernetesNetworkPlugin"
                :options="formData.KubernetesNetworkPlugin"
                optionLabel="value"
                placeholder="Kubernetes network plugin to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Container Manager</h5>
                <Dropdown
                v-model="formData.selectedContainerManager"
                :options="formData.ContainerManager"
                optionLabel="value"
                placeholder="Container manager to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
            </div>
          </div>
          <div v-show="formData.deploy_kubernetes">
            <div class="p-formgroup-inline">
              <div class="p-field p-col-3">
                <h5>Dashboard Enable</h5>
                <Dropdown
                v-model="formData.selectedDashboardEnable"
                :options="formData.DashboardEnable"
                optionLabel="value"
                placeholder="Dashboard enable to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>HEML Enable</h5>
                <Dropdown
                v-model="formData.selectedHEMLEnable"
                :options="formData.HEMLEnable"
                optionLabel="value"
                placeholder="HEML enable to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Registry Enable</h5>
                <Dropdown
                v-model="formData.selectedRegistryEnable"
                :options="formData.RegistryEnable"
                optionLabel="value"
                placeholder="Registry enable to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
            </div>
          </div>
          <div v-show="formData.deploy_kubernetes">
            <div class="p-formgroup-inline">
              <div class="p-field p-col-3">
                <h5>Ingress Nginx Enabled</h5>
                <Dropdown
                v-model="formData.selectedIngressNginxEnabled"
                :options="formData.IngressNginxEnabled"
                optionLabel="value"
                placeholder="Ingress nginx enabled to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Ingress Nginx Host Network</h5>
                <Dropdown
                v-model="formData.selectedIngressNginxHostNetwork"
                :options="formData.IngressNginxHostNetwork"
                optionLabel="value"
                placeholder="Ingress nginx host network to choose..."
                :filter="true"
                :showClear="true"
               />
              </div>
              <div class="p-field p-col-3">
                <h5>Krew Enabledr</h5>
                <Dropdown
                v-model="formData.selectedKrewEnabled"
                :options="formData.KrewEnabled"
                optionLabel="value"
                placeholder="Krew enabled to choose..."
                :filter="true"
                :showClear="true"
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
export default {
  components: {
    Dropdown
  },
  data () {
    return {
      selectedKubernetesInstallMethod: this.formData.selectedKubernetesInstallMethod,
      selectedKubernetesVersion: null,
      selectedKubernetesNetworkPlugin: null,
      selectedContainerManager: null,
      selectedDashboardEnable: null,
      selectedHEMLEnable: null,
      selectedRegistryEnable: null,
      selectedIngressNginxEnabled: null,
      selectedIngressNginxHostNetwork: null,
      selectedKrewEnabledr: null,
      deploy_kubernetes: this.formData.deploy_kubernetes,
      deploy_kubernetes_v2: false,
      height: this.formData.deploy_kubernetes ? 700 : 400
    }
  },
  props: {
    formData: Object
  },
  methods: {},
  watch: {
    deploy_kubernetes: function () {
      this.formData.deploy_kubernetes = false
      this.formData.deploy_kubernetes_v2 = this.deploy_kubernetes_v2
      // this.formData.deploy_kubernetes = this.deploy_kubernetes
      // if (this.deploy_kubernetes === true) {
      //   this.height = 700
      // } else {
      //   this.height = 400
      // }
    },
    selectedKubernetesInstallMethod: function () {
      this.formData.selectedKubernetesInstallMethod = this.selectedKubernetesInstallMethod
      if (this.selectedKubernetesInstallMethod !== null && this.selectedKubernetesInstallMethod.value === 'vm') {
        this.formData.vm_deploy_args = true
      } else {
        this.formData.vm_deploy_args = false
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
