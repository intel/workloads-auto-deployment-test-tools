/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import 'primevue/resources/themes/fluent-light/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

import Tooltip from 'primevue/tooltip'
import Vuelidate from 'vuelidate'
import ToastService from 'primevue/toastservice'
import PrimeVue from 'primevue/config'
import Clipboard from 'clipboard'
import ConfirmationService from 'primevue/confirmationservice'

Vue.use(PrimeVue)
Vue.config.productionTip = false
Vue.prototype.Clipboard = Clipboard
Vue.directive('tooltip', Tooltip)
Vue.use(Vuelidate)
Vue.use(ToastService)
Vue.use(ConfirmationService)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
