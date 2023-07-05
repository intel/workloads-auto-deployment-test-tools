<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div>
    <Card>
    <template #content>
      <MarkdownDisplayComponent :markdown='content'/>
    </template>
    </Card>
  </div>
</template>

<script>

import Card from 'primevue/card'
import MarkdownDisplayComponent from '@/components/MarkdownDisplay'

export default {
  name: 'GuideUserComponent',

  components: {
    Card,
    MarkdownDisplayComponent
  },

  data () {
    return {
      content: `
# TaaS User Guide



`
    }
  }
}
</script>
