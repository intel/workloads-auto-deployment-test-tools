#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
from django.apps import AppConfig


class LocalConfig(AppConfig):
    name = 'local'

    def ready(self):
        import local.signals
