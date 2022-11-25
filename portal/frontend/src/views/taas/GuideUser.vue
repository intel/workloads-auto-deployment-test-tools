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
