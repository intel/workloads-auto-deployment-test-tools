<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
<div>
  <ScrollPanel style="width: 100%;" class="custom">
    <pre>{{ log }}</pre>
  </ScrollPanel>
</div>
</template>

<script>
import ScrollPanel from 'primevue/scrollpanel'

import axios from 'axios'

export default {
  name: 'LocalLogComponent',
  components: {
    ScrollPanel
  },
  props: {
    LogPath: String
  },
  data () {
    return {
      errors: [],
      polling: null,
      log: null
    }
  },
  methods: {
    getLog () {
      const endpoint = '/local/api/get_config_json/?json_file=' + this.LogPath
      axios
        .get(endpoint)
        .then(response => {
          this.log = response.data
        })
        .catch(e => {
          this.errors.push(e)
          if (e.response.status === 404) {
            this.log = 'The test run log is not created yet. Please wait for the job to start or rebuild it.'
          } else {
            this.log = e
          }
        })
    },
    pollData () {
      this.polling = setInterval(() => {
        this.getLog()
      }, 10000)
    }
  },
  created () {
    this.getLog()
    this.pollData()
  },
  beforeDestroy () {
    clearInterval(this.polling)
  }
}
</script>

<style scoped>
</style>
