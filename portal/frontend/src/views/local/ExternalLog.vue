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
  name: 'LocalExternalLogComponent',
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
      const endpoint = `/local/api/provision_log/?job_id=${this.LogPath}`
      const config = { 'Cache-Control': 'no-store' }
      axios
        .get(endpoint, config)
        .then(response => {
          this.log = response.data[0].data
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
      }, 100000)
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
