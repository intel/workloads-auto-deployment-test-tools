<template>
  <div id="app">
    <div id="nav" v-if="$route.name.indexOf('Local') !== -1">
      <NavbarLocalComponent/>
    </div>
    <div id="nav" v-else>
      <NavbarComponent/>
    </div>
    <router-view/>
  </div>
</template>

<script>

import NavbarLocalComponent from './components/NavbarLocal.vue'
import NavbarComponent from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    NavbarComponent,
    NavbarLocalComponent
  }
}
</script>

<style>
  #app {
    font-family: Roboto, Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, Lucida Grande, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    font-size: 90%;
  }
  .p-column-title {
    font-size: 80%;
    text-align: center;
  }
  .p-rowgroup-header {
    font-weight: bold;
  }
  .error {
    font-size: 0.75rem;
    line-height: 1;
    margin-top: 2px;
    display: block;
    color: #f57f6c;
  }
  .note {
    font-size: 0.75rem;
    line-height: 1;
    margin-top: 2px;
    display: block;
    color: #7797f1;
  }
  .p-panel-content {
    font-size: 0.75rem;
  }
</style>
