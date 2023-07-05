#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
python3 manage.py makemigrations
python3 manage.py migrate --no-input
python3 manage.py collectstatic --noinput
python3 manage.py runsslserver --certificate ./cert/cert.pem --key ./cert/key.pem 0.0.0.0:8899
