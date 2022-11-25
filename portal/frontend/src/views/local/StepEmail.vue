<template>
  <div align="center">
  <div class="p-field p-col-6 p-md-6 text-align-left">
    <el-card class="box-card" style="height: 400px;">
      <div slot="header" class="clearfix">
        <span>VM Args</span>
      </div>
      <div>
        <el-form label-position="right" label-width="80px" :model="formData">
          <div class="p-formgroup-inline">
            <div class="p-field p-col-5">
              <h5>Sender Email</h5>
              <InputText
              type="text"
              v-model="formData.SenderEmail"
              />
            </div>
            <div class="p-field p-col-5">
              <h5>Receiver Email</h5>
              <InputText
              type="text"
              v-model="formData.ReceiverEmail"
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
      selectedController: null,
      workloads: null,
      selectedVersion: null,
      versions: null,
      vm_deploy_args: true
    }
  },
  props: {
    formData: Object
  },
  methods: {}
}
</script>

<style scoped>
.text-align-left {
  text-align: left;
}
</style>
