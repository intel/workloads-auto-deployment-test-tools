<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <Message :severity="this.messageType" v-show="this.isShowMessage">{{ message }}</Message>
    <Menubar :model='items' class="font-menu">
      <template #start>
        <div style="display: flex!important;">
            <img title="Here is homepage" alt='logo' src="@/assets/wsf_logo.svg" class='logo-image' style="max-width: 7rem;padding-left:2rem;" @click="clickLogo" />
            <img title="Here is homepage" alt='logo' src="@/assets/wsf_logo.png" class='logo-image' @click="clickLogo"/>
        </div>
      </template>
      <template #end>
        <LoginUserComponent />
      </template>
    </Menubar>
  </div>
</template>

<script>
import Menubar from 'primevue/menubar'
import Message from 'primevue/message'
import LoginUserComponent from '@/components/LoginUser.vue'
import axios from 'axios'

export default {
  name: 'NavbarLocalComponent',
  components: {
    Menubar,
    Message,
    LoginUserComponent
  },
  data() {
    return {
      errors: [],
      message: '',
      isShowMessage: false,
      messageType: '',
      items: [
        {
          label: 'Home',
          // icon: 'pi pi-fw pi-home',
          to: '/'
        },
        {
          label: 'Job',
          // icon: 'pi pi-fw pi-book',
          to: '/local/job'
        },
        {
          label: 'Instance',
          // icon: 'pi pi-fw pi-desktop',
          to: '/local/instance'
        },
        {
          label: 'Dashboard',
          // icon: 'pi pi-fw pi-chart-line',
          command: () => {
            this.openPage('dashboard')
          }
        },
        {
          label: 'Provision',
          // icon: 'pi pi-fw pi-flag',
          to: '/local/provision'
        },
        {
          label: 'Config template',
          // icon: 'pi pi-fw pi-file',
          to: '/local/config'
        },
        {
          label: 'Admin',
          // icon: 'pi pi-fw pi-user',
          url: '/admin/',
          target: '_blank'
        }
      ]
    }
  },
  methods: {
    showMessage(messageType, message) {
      this.messageType = messageType
      this.message = message
      this.isShowMessage = true
    },
    openPage(urlName) {
      const endpoint = '/local/api/local_setting/'
      axios.get(endpoint, {
        params: {
          name: urlName + '_url'
        }
      })
        .then(response => {
          if (response.data.length === 0) {
            this.showMessage('warn', 'There is no ' + urlName + ' in database')
          } else {
            console.log(response.data)
            window.open(response.data[0].value)
          }
        })
        .catch(e => {
          this.errors.push(e)
          this.showMessage('error', 'Something goes wrong')
        })
    },
    clickLogo() {
      this.$router.push({
        path: '/'
      })
    }
  }
}
</script>
