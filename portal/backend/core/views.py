#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class IndexTemplateView(LoginRequiredMixin, TemplateView):

    def get_template_names(self):
        if settings.DEBUG:
            template_name = 'index-dev.html'
        else:
            template_name = 'index.html'
        return template_name
