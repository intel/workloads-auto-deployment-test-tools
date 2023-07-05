#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

function Run () {
	REPONAME="BIOSManager"
	cd "$REPONAME"
	./runinconda.sh
	cd -
}

./init.sh
Run

