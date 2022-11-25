<template>
<div>
  <Menubar :model='items'>
    <template #start>
      <img alt='logo' src="/static/img/logo.jpg" height='40' class='p-mr-2' />
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
  name: 'NavbarLocalComponent',
  components: {
    Menubar,
    LoginUserComponent
  },
  data () {
    return {
      items: [
        {
          label: 'Home',
          icon: 'pi pi-fw pi-home',
          to: '/'
        },
        {
          label: 'Job',
          icon: 'pi pi-fw pi-book',
          to: '/local/job'
        },
        {
          label: 'Instance',
          icon: 'pi pi-fw pi-cloud',
          to: '/local/instance'
        },
        {
          label: 'Provision',
          icon: 'pi pi-fw pi-cloud',
          to: '/local/provision'
        },
        {
          label: 'Config template',
          icon: 'pi pi-fw pi-cloud',
          to: '/local/config'
        },
        {
          label: 'Admin',
          icon: 'pi pi-fw pi-user',
          url: '/admin/',
          target: '_blank'
        }
      ]
    }
  }
}
</script>
