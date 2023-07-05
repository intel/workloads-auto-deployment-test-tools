#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
export DJANGO_SETTINGS_MODULE=taas.settings_dev

python3 manage.py runsslserver 0.0.0.0:8899
