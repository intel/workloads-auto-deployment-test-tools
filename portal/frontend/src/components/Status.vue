<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <Tag
      severity="success"
      :value="status"
      rounded
      v-if="status === 'PASS'"
    />
    <Tag
      severity="danger"
      :value="status"
      rounded
      v-else-if="status === 'FAILED'"
    />
    <Tag
      severity="info"
      :value="status"
      rounded
      v-else-if="status === 'NOT_START'"
    />
    <Tag
      severity="warning"
      :value="status"
      rounded
      v-else-if="status === 'RUNNING'"
    />
    <!-- For auto support matrix -->
    <Tag
      severity="warning"
      :value="status"
      rounded
      v-else-if="status === 'TODO'"
    />
    <Tag
      severity="success"
      :value="status"
      rounded
      v-else-if="status === 'DONE'"
    />
    <Tag
      severity="info"
      :value="status"
      rounded
      v-else-if="status === 'NA'"
    />
    <Tag
      severity="primary"
      :value="status"
      rounded
      v-else
    />
  </div>
</template>

<script>
import Tag from 'primevue/tag'

export default {
  name: 'Status',
  components: {
    Tag
  },
  props: {
    status: String
  }
}
</script>

<style scoped>
  .p-tag {
    width: 9em;
  }
</style>
