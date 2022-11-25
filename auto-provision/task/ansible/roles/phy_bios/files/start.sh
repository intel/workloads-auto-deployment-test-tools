#!/usr/bin/env bash

function Run () {
	REPONAME="BIOSManager"
	cd "$REPONAME"
	./runinconda.sh
	cd -
}

./init.sh
Run

