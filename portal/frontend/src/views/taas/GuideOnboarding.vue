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
  name: 'GuideOnboardingComponent',

  components: {
    Card,
    MarkdownDisplayComponent
  },

  data () {
    return {
      content: `
# TaaS Onboarding Guide

This file is a best pratice for first run on Taas. Please follow the suggested convention in this guide in order to run it smoothly in TaaS.
`
    }
  }
}
</script>
