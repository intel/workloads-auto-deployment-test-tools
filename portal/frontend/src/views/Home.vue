<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div class="home-background">
    <Message class="ml-2 mr-2" severity="warn" v-show="!allowToSubmitJob">
      <h5>NOT allow to submit job due to maintenance mode or set on purpose</h5>
    </Message>
    <div class="boxes">
      <h1 class="mb-4 home-title">Intel® Toolkit for Workload Deployment & Testing</h1>
      <div class="p-shadow-7 box button-6">
        <h2>
          <a href="/local/job">PROVISION
            <span class="link-spanner"></span>
          </a>
        </h2>
        <img src="/static/img/platform.png" alt="local">
      </div>
    </div>
  </div>
</template>

<script>
import 'primeflex/primeflex.css'
import Message from 'primevue/message'

export default {
  name: 'HomeTaas',
  components: {
    Message
  },
  data() {
    return {
      allowToSubmitJob: true
    }
  }
}
</script>