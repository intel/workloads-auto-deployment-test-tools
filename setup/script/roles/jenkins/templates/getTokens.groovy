/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
import hudson.model.*
import jenkins.model.*
import jenkins.security.*
import jenkins.security.apitoken.*

def userName="admin"

user = User.get(userName)

def prop = user.getProperty(ApiTokenProperty.class)
// the name is up to you
def tokenList= prop.getTokenStore().getTokenListSortedByName()

tokenList.each() {

  println it.name + " uuid: "+ it.uuid

}