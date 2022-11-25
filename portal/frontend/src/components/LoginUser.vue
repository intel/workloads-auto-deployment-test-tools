<template>
  <div>
    <span class="user">{{ loginUser }} / </span>
    <a
      class="mr-4 btn btn-primary btn-sm"
      href="/accounts/logout/"
    >
      Logout
    </a>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginUserComponent',
  data () {
    return {
      loginUser: null,
      errors: []
    }
  },
  methods: {
    getLoginUser () {
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
  created () {
    this.getLoginUser()
  }
}
</script>

<style scoped>
  .user {
      display: inline-block;
      padding: .35em .65em;
      font-size: .75em;
      font-weight: 700;
      line-height: 1;
      text-align: center;
      white-space: nowrap;
      vertical-align: baseline;
      border-radius: .25rem;
  }
</style>
