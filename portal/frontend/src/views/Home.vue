<template>
<div>
  <Message
    class="ml-2 mr-2"
    severity="warn"
    v-show="!allowToSubmitJob"
  >
    <h5>NOT allow to submit job due to maintenance mode or set on purpose</h5>
  </Message>
  <div class="boxes">
    <h3 class="mb-4">WiE Validation as a Service</h3>
    <div class="p-shadow-7 box">
      <h2>
        <a href="/local/job">Local
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
  data () {
    return {
      allowToSubmitJob: true
    }
  }
}
</script>

<style scoped>
.boxes {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translateX(-50%) translateY(-50%);
  white-space: nowrap;
  text-align: center;
}

.box {
  display: inline-block;
  width: 250px;
  height: 250px;
  margin: 20px;
  padding: 10px;
  position: relative;
}

.box a {
  display: block;
  padding: 12px 16px 12px 16px;
  text-decoration: none;
  color: #2c3e50;
}

.link-spanner {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;

  /* edit: fixes overlap error in IE7/8,
     make sure you have an empty gif
  background-image: url('empty.gif');*/
}

.box:hover {
  background-color: bisque;
}
</style>
