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
  name: 'NavbarComponent',
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
          label: 'Local',
          icon: 'pi pi-fw pi-book',
          to: '/local/job'
        },
        {
          label: 'Admin',
          icon: 'pi pi-fw pi-user',
          url: '/admin/',
          target: '_blank'
        },
        {
          label: 'API',
          icon: 'pi pi-fw pi-book',
          url: '/swagger/',
          target: '_blank'
        },
        {
          label: 'Guide',
          icon: 'pi pi-fw pi-book',
          items: [
            {
              label: 'User Guide',
              icon: 'pi pi-fw pi-book',
              to: '/guide/user'
            },
            {
              label: 'Admin Guide',
              icon: 'pi pi-fw pi-book',
              to: '/guide/admin'
            },
            {
              label: 'Onboarding Guide',
              icon: 'pi pi-fw pi-book',
              to: '/guide/onboarding'
            }
          ]
        }
      ]
    }
  }
}
</script>
