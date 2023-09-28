#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

# Fix synk scanned openssl/libcrypto3 issue
# https://hub.docker.com/layers/library/node/lts-alpine3.18/images/sha256-c8245ebe9d86862ab40bbaee04f69f9787c57b83beb6e9a174e8afc154989e1f?context=explore
FROM node:lts-alpine3.18

ENV CONTAINER_PATH /frontend
ARG https_proxy
ARG http_proxy

WORKDIR $CONTAINER_PATH

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

EXPOSE 8080

CMD ["npm", "run", "build"]
# CMD ["npm", "run", "serve"]

