<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div v-html="processedMarkdown"></div>
</template>

<script>
import { marked } from 'marked'
import highlight from 'highlight.js'
import 'highlight.js/styles/solarized-dark.css'

export default {
  name: 'MarkdownDisplayComponent',
  computed: {
    processedMarkdown () {
      return marked.defaults(this.markdown, {
        highlight (md) {
          return highlight.highlightAuto(md).value
        }
      })
    }
  },
  props: {
    markdown: String
  }
}
</script>

<style>

</style>
