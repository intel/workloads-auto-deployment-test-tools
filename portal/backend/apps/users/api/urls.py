#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
from django.urls import path
from .views import CurrentUserAPIView

urlpatterns = [
    path('user/', CurrentUserAPIView.as_view(), name='current-user')
]
