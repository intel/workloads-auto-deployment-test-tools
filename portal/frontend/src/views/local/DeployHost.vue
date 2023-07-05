<!--
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
-->
<template>
<div>
    <Card  class="p-card-background">
        <template slot="content">
            <div class="p-field p-col-2">
                <h5>Workload</h5>
            </div>
        </template>
    </Card>
</div>
</template>

<script>
import Card from 'primevue/card'

export default {
  components: {
    Card
  },
  props: {
    formData: Object
  },
  methods: {}
}
</script>
