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
  name: 'GuideAdminComponent',

  components: {
    Card,
    MarkdownDisplayComponent
  },

  data () {
    return {
      content: `
# TaaS Admin Guide

This document is to guide administrator to do some maintenance jobs on TaaS

`
    }
  }
}
</script>
