<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <span class="user">{{ loginUser }} / </span>
    <a class="mr-4 btn btn-primary btn-sm logout-button" href="/accounts/logout/">
      Logout
    </a>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginUserComponent',
  data() {
    return {
      loginUser: null,
      errors: []
    }
  },
  methods: {
    getLoginUser() {
      const endpoint = '/users/api/user/'
      axios
        .get(endpoint)
        .then(response => {
          this.loginUser = response.data.username
        })
        .catch(e => {
          this.errors.push(e)
        })
    }
  },
  created() {
    this.getLoginUser()
  }
}
</script>