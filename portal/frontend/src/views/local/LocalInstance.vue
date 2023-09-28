<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <ConfirmDialog class="font"></ConfirmDialog>
    <div class="font" v-show="!showtestcases">
      <div>
        <DataTable class="font table" responsiveLayout="scroll" :value='instances'
          columnResizeMode="fit" :paginator='true' :filters="filters" :loading="loading" :rows='20'
          :expandedRows.sync="expandedRows" dataKey="id"
          paginatorTemplate='CurrentPageReport FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown'
          :rowsPerPageOptions='[20, 50, 100]' currentPageReportTemplate='Showing {first} to {last} of {totalRecords}'>
          <template #header class="p-datatable-header">
            <div class="title-header">
              <div class="title-header-left">
                <h4 class="m-0"><b>Servers</b></h4>
              </div>
              <div class="title-header-right">
                <span class="p-input-icon-left">
                  <i class="pi pi-search" />
                  <InputText class="p-inputtext-sm font" v-model="filters['global']['value']"
                    placeholder="Global Search" />
                  <Button type="button" icon="pi pi-refresh" class="p-button-text font" @click="refresh" />
                </span>
              </div>
            </div>
          </template>
          <template #empty>
            No Instance found.
          </template>
          <template #loading>
            Loading instance data. Please wait.
          </template>
          <Column :expander="true" :headerClass="'column-header'" bodyClass="column-body"/>
          <Column v-for="col of columns" :headerClass="'column-header'" bodyClass="column-body" :field="col.field"
            :header="col.header" :key="col.field" :hidden="col.hidden" :sortable="col.sortable">
            <template #body="slotProps" v-if="col.field === 'status'">
              <Button class="p-button-raised p-button-rounded p-button-success p-button-sm"
                :label="slotProps.data.status" v-if="slotProps.data.status === 'FREE'">
              </Button>
              <Button class="p-button-raised p-button-rounded p-button-info p-button-sm button"
                :label="slotProps.data.status" v-else-if="slotProps.data.status === 'DELETED'">
              </Button>
              <Button class="p-button-warning p-button-sm p-button-raised p-button-rounded button"
                :label="slotProps.data.status" v-else-if="slotProps.data.status === 'DELETING'">
              </Button>
              <Button class="p-button-danger p-button-sm p-button-raised p-button-rounded button"
                :label="slotProps.data.status" v-else-if="slotProps.data.status === 'IN_USE'">
              </Button>
              <Button class="p-button-danger p-button-sm p-button-raised p-button-rounded button"
                :label="slotProps.data.status" v-else-if="slotProps.data.status === 'CREATE_FAILED'">
              </Button>
              <Button class="p-button-info p-button-sm p-button-rounded button" :label="slotProps.data.status" v-else>
              </Button>
            </template>
            <template #body="slotProps" v-else-if="col.field === 'username'">
              <Button id="copy_text" icon="pi pi-users" class="p-button-rounded" @click="copy"
                :data-clipboard-text="slotProps.data.username" v-if="slotProps.data.username !== null">
              </Button>
            </template>
            <template #body="slotProps" v-else-if="col.field === 'password'">
              <Button id="copy_text" icon="pi pi-check" class="p-button-rounded" @click="copy"
                :data-clipboard-text="slotProps.data.password" v-if="slotProps.data.password !== null">
              </Button>
            </template>
          </Column>
          <template #expansion="slotProps">
            <div class="orders-subtable">
              <h5>Job Queue for machine {{ slotProps.data.ip }}</h5>
              <LocalJobInstanceQueue :ip="slotProps.data.ip" />
            </div>
          </template>
          <template #paginatorRight>
            <Button type='button' icon='pi pi-cloud' class='p-button-text' />
          </template>
        </DataTable>
      </div>
    </div>
    <Dialog :header="'instance ' + log" :visible.sync="displayTestLog" :style="{ width: '90%' }" :maximizable="false"
      :modal="true" v-if="log !== null">
      <CloudLogComponent :LogPath="log" />
    </Dialog>
    <Dialog :header="'Actions for instance'" :visible.sync="displayAction" :style="{ width: '20%' }" :maximizable="false"
      :modal="true" v-if="displayAction">
      <Menu :model="items"></Menu>
    </Dialog>
    <Dialog :header="'Duration extention Days'" :visible.sync="displayExtention" :style="{ width: '20%' }"
      :maximizable="false" :modal="true" v-if="displayExtention">
      <InputText v-model="selectedDuration" placeholder="Days to Extend" class="p-inputtext-sm" size="10" />
      <Button class="p-button-raised p-button-rounded p-button-success p-button-sm" label="EXTEND"
        @click="extendDuration(instanceId); displayExtention = false" />
    </Dialog>
    <Toast position="top-right" />
  </div>
</template>

<script>
import DataTable from 'primevue/datatable'
import Toast from 'primevue/toast'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
// import Tag from 'primevue/tag'
import ConfirmDialog from 'primevue/confirmdialog'
// import OverlayPanel from 'primevue/overlaypanel'
import InputText from 'primevue/inputtext'
import { CSRF_TOKEN } from '../../common/csrf_token'
import Clipboard from 'clipboard'
import LocalLogComponent from '@/views/local/TestLog.vue'
import Menu from 'primevue/menu'
import LocalJobInstanceQueue from '@/views/local/LocalJobInstanceQueue.vue'

// import SpeedDial from 'primevue/speeddial'

import axios from 'axios'

export default {
  name: 'LocalInstance',
  components: {
    DataTable,
    Column,
    Button,
    ConfirmDialog,
    // OverlayPanel,
    InputText,
    Dialog,
    // Tag,
    LocalLogComponent,
    LocalJobInstanceQueue,
    Menu,
    Toast
    // SpeedDial
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
      instanceId: null,
      jenkinsId: null,
      expandedRows: null,
      region: null,
      status: null,
      displayTestLog: false,
      displayAction: false,
      displayExtention: false,
      duration: null,
      instances: [],
      testsets: [],
      showtestcases: false,
      selectedDuration: null,
      jobid: null,
      columns: null,
      log: null,
      items: null
    }
  },
  methods: {
    getInstances() {
      const endpoint = '/local/api/instance/'
      axios
        .get(endpoint)
        .then(response => {
          this.instances = response.data
          this.loading = false
        })
        .catch(e => {
          this.errors.push(e)
        })
    },

    updateInstanceStatus(id) {
      const endpoint = `/local/api/instance/${id}/`
      const config = {
        headers: {
          'content-type': 'application/json',
          'X-CSRFTOKEN': CSRF_TOKEN
        }
      }
      const data = {
        status: 'DELETING'
      }
      axios
        .put(endpoint, data, config)
        .then(response => {
        })
        .catch(e => {
          this.errors.push(e)
          console.log(e)
        })
    },

    updateActions() {
      console.log(this.status)
      if (this.status !== 'CREATED' && this.status !== 'CREATE_FAILED') {
        this.items = [
          {
            label: 'Logs',
            items: [
              {
                label: 'Jenkins Log',
                icon: 'pi pi-external-link',
                target: '_blank',
                command: () => {
                  window.open('http://172.17.120.39:8080/job/ServicesFramework/job/post-silicon-validation/job/cloud_online_debug/' + this.jenkinsId, '_blank')
                }
              },
              {
                label: 'Delete Log',
                icon: 'pi pi-external-link',
                command: () => {
                  this.actions()
                  this.log = this.instanceId + '_delete.log'
                }
              },
              {
                label: 'Monitor Log',
                icon: 'pi pi-external-link',
                command: () => {
                  this.displayTestLog = true
                  this.log = this.instanceId + '_change.log'
                }
              }
            ]
          }
        ]
      } else {
        this.items = [
          {
            label: 'Logs',
            items: [
              {
                label: 'Jenkins Log',
                icon: 'pi pi-external-link',
                target: '_blank',
                command: () => {
                  window.open('http://172.17.120.39:8080/job/ServicesFramework/job/post-silicon-validation/job/cloud_online_debug/' + this.jenkinsId, '_blank')
                }
              },
              {
                label: 'Delete Log',
                icon: 'pi pi-external-link',
                command: () => {
                  this.actions()
                  this.log = this.instanceId + '_delete.log'
                }
              },
              {
                label: 'Monitor Log',
                icon: 'pi pi-external-link',
                command: () => {
                  this.displayTestLog = true
                  this.log = this.instanceId + '_change.log'
                }
              }
            ]
          },
          {
            label: 'Actions',
            items: [
              {
                label: 'Delete',
                icon: 'pi pi-times',
                command: () => {
                  this.deleteInstance(this.instanceId)
                }
              },
              {
                label: 'Extend',
                icon: 'pi pi-external-link',
                command: () => {
                  this.displayExtention = true
                  this.displayAction = false
                }
              }
            ]
          }
        ]
      }
    },

    extendDuration(id) {
      const endpoint = `/cloud/api/instance/${id}/`
      const config = {
        headers: {
          'content-type': 'application/json',
          'X-CSRFTOKEN': CSRF_TOKEN
        }
      }
      console.log(this.selectedDuration, this.duration)
      const data = {
        duration: parseInt(this.selectedDuration) + this.duration
      }
      axios
        .put(endpoint, data, config)
        .then(response => {
          this.refresh()
        })
        .catch(e => {
          this.errors.push(e)
          console.log(e)
        })
    },

    showTestCases(jobid) {
      this.showtestcases = true
      this.jobid = jobid.toString()
    },

    actions(instanceId, jekinsId) {
      this.displayTestLog = true
    },

    refresh() {
      this.getInstances()
    },

    deleteInstance(id) {
      this.$confirm.require({
        message: 'Are you sure you want to proceed?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
          this.updateInstanceStatus(id)
          this.displayAction = false
          this.refresh()
        },
        reject: () => {
          this.displayAction = false
          this.refresh()
        }
      })
    },

    copy() {
      var clipboard = new Clipboard('#copy_text')
      clipboard.on('success', (e) => {
        this.$toast.add({ severity: 'success', summary: 'COPY', detail: 'INFO COPYED', life: 3000 })
        clipboard.destroy()
      })
      clipboard.on('error', (e) => {
        this.$toast.add({ severity: 'success', summary: 'COPY', detail: 'INFO COPYED', life: 3000 })
        clipboard.destroy()
      })
    }
    // toggle (event) {
    //   this.$refs.ops.toggle(event)
    // }
  },
  created() {
    this.columns = [
      { field: 'id', header: 'ID' },
      // { field: 'name', header: 'NAME' },
      { field: 'ip', header: 'IP' },
      { field: 'username', header: 'USERNAME' },
      { field: 'password', header: 'PASSWORD' },
      { field: 'region', header: 'REGION', sortable: true },
      { field: 'instance_type', header: 'TYPE', sortable: true },
      { field: 'cpu_core', header: 'CPU CORE', sortable: true },
      { field: 'cpu_model', header: 'Model', sortable: true },
      { field: 'cpu_arch', header: 'CPU ARCH', sortable: true },
      { field: 'os', header: 'OS', sortable: true },
      { field: 'k8s_role', header: 'ROLE', sortable: true },
      { field: 'k8s_controller', header: 'Controller', sortable: true },
      { field: 'status', header: 'STATUS' },
      { field: 'user', header: 'User' },
      // { field: 'jenkins_id', header: 'JENKINS', hidden: true },
      { field: 'created', header: 'Created' }
    ]
    this.getInstances()
  }
}
</script>

<style lang="scss" scoped>
.p-button-sm {
  width: 8em;
}

.op {
  font-style: normal;
  font-size: 0.75rem;
  letter-spacing: normal;
  line-break: auto;
  text-shadow: none;
  text-transform: none;
  white-space: normal;
  word-break: normal;
  word-spacing: normal;
  word-wrap: normal;
  text-decoration: none;
  background-color: #363636;
  color: #ffffff;
}

.tag {
  width: 10em;
}

.button {
  width: 10em;
}
.p-button.p-button-warning, .p-buttonset.p-button-warning > .p-button, .p-splitbutton.p-button-warning > .p-button  {
    color: white !important;
    background: rgb(0, 120, 212) !important;
  }

</style>
