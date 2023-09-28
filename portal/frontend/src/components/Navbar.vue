<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <Menubar :model='items' class="font-menu">
      <template #start>
        <div style="display: flex!important;">
            <img title="Here is homepage" alt='logo' src="@/assets/wsf_logo.svg" class='logo-image' style="max-width: 7rem;padding-left:2rem;"/>
            <img title="Here is homepage" alt='logo' src="@/assets/wsf_logo.png" class='logo-image' />
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

import LoginUserComponent from '@/components/LoginUser.vue'

export default {
  name: 'NavbarComponent',
  components: {
    Menubar,
    LoginUserComponent
  },
  data() {
    return {
      items: [
        {
          label: 'Home',
          to: '/'
        },
        {
          label: 'Provision',
          to: '/local/job'
        },
        {
          label: 'Admin',
          url: '/admin/',
          target: '_blank'
        },
        {
          label: 'API',
          url: '/swagger/',
          target: '_blank'
        },
        {
          label: 'Guide',
          items: [
            {
              label: 'User Guide',
              to: 'https://github.com/intel/workloads-auto-deployment-test-tools/tree/main/doc/EN/user-guide.md'
            }
          ]
        }
      ]
    }
  }
}
</script>
