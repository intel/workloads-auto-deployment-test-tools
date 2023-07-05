/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
import Vue from 'vue'
import VueRouter from 'vue-router'

import HomeTaas from '../views/Home.vue'

import GuideAdminComponent from '../views/taas/GuideAdmin.vue'
import GuideOnboardingComponent from '../views/taas/GuideOnboarding.vue'
import GuideUserComponent from '../views/taas/GuideUser.vue'

import LocalJob from '../views/local/LocalJob.vue'
import LocalInstance from '../views/local/LocalInstance.vue'
import LocalConfig from '../views/local/LocalConfig.vue'
import LocalProvision from '../views/local/LocalProvision.vue'
import DeployHost from '../views/local/DeployHost.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeTaas
  },
  {
    path: '/guide/admin',
    name: 'GuideAdmin',
    component: GuideAdminComponent
  },
  {
    path: '/guide/onboarding',
    name: 'GuideOnboarding',
    component: GuideOnboardingComponent
  },
  {
    path: '/guide/user',
    name: 'GuideUser',
    component: GuideUserComponent
  },
  {
    path: '/local/job',
    name: 'LocalJob',
    component: LocalJob
  },
  {
    path: '/local/instance',
    name: 'LocalInstance',
    component: LocalInstance
  },
  {
    path: '/local/config',
    name: 'LocalConfig',
    component: LocalConfig
  },
  {
    path: '/local/provision',
    name: 'LocalProvision',
    component: LocalProvision
  },
  {
    path: '/local/deployhost',
    name: 'DeployHost',
    component: DeployHost
  }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
