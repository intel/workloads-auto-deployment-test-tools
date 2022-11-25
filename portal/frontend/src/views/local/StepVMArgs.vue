<template>
  <div align="center">
  <div class="p-field p-col-9 p-md-9 text-align-left">
    <el-card class="box-card" v-bind:style="{'height': height +'px'}">
      <div slot="header" class="clearfix">
        <span>VM Args</span>
      </div>
      <div>
        <el-form label-position="right" label-width="80px" :model="formData">
          <div class="p-formgroup-inline">
            <div class="p-field p-col-6">
              <h5>VM Deploy Args</h5>
              <el-switch
              v-model="vm_deploy_args"
              active-color="#13ce66"
              inactive-color="#ff4949"
              :disabled="this.switchEnable">
              </el-switch>
            </div>
          </div>
          <div class="p-field p-col-3" v-show="vm_deploy_args">
            <h5>VM Docker</h5>
            <Dropdown
            v-model="formData.selectedVMDocker"
            :options="formData.VMDocker"
            optionLabel="value"
            placeholder="VM docker to choose..."
            :filter="true"
            :showClear="true"
            />
          </div>
          <div class="p-formgroup-inline" v-show="vm_deploy_args">
            <div class="p-field p-col-3">
              <h5>OS Number</h5>
              <Dropdown
              v-model="formData.selectedOSNumber"
              :options="formData.OSNumber"
              optionLabel="value"
              placeholder="OS number to choose..."
              :filter="true"
              :showClear="true"
              />
            </div>
            <div class="p-field p-col-3">
              <h5>OS Type</h5>
              <Dropdown
              v-model="formData.selectedOSType"
              :options="formData.OSType"
              optionLabel="value"
              placeholder="OS type to choose..."
              :filter="true"
              :showClear="true"
              />
            </div>
            <div class="p-field p-col-3">
              <h5>VM Name</h5>
              <InputText
              type="text"
              v-model="formData.selectedVMName"
              />
            </div>
          </div>
          <div class="p-formgroup-inline" v-show="vm_deploy_args">
            <div class="p-field p-col-3">
              <h5>Memory</h5>
              <Dropdown
              v-model="formData.selectedMemory"
              :options="formData.Memory"
              optionLabel="value"
              placeholder="Memory to choose..."
              :filter="true"
              :showClear="true"
              />
            </div>
            <div class="p-field p-col-3">
              <h5>CPU Number</h5>
              <Dropdown
              v-model="formData.selectedCPUNumber"
              :options="formData.CPUNumber"
              optionLabel="value"
              placeholder="CPU number to choose..."
              :filter="true"
              :showClear="true"
              />
            </div>
            <div class="p-field p-col-3">
              <h5>Disk</h5>
              <Dropdown
              v-model="formData.selectedDisk"
              :options="formData.Disk"
              optionLabel="value"
              placeholder="Disk to choose..."
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
import InputText from 'primevue/inputtext'
export default {
  components: {
    Dropdown,
    InputText
  },
  data () {
    return {
      vm_deploy_args: this.formData.vm_deploy_args && this.formData.deploy_kubernetes,
      switchEnable: (this.formData.selectedKubernetesInstallMethod.value !== 'vm') || !this.formData.deploy_kubernetes,
      selectedVMDocker: null,
      selectedOSNumber: null,
      selectedOSType: null,
      selectedVMName: null,
      selectedMemory: null,
      selectedCPUNumber: null,
      selectedDisk: null,
      height: this.formData.vm_deploy_args ? 700 : 400
    }
  },
  props: {
    formData: Object
  },
  methods: {},
  watch: {
    vm_deploy_args: function () {
      this.formData.vm_deploy_args = this.vm_deploy_args
      if (this.vm_deploy_args === true) {
        this.height = 700
      } else {
        this.height = 400
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
