#!/bin/bash

# Update publicPath ip address in frontend/vue.config.js file to dev server
DEV_IP=$(hostname -I | awk '{print $1}')
sed -i "s~publicPath:\ 'http://0.0.0.0:8080/'~publicPath:\ 'http://${DEV_IP}:8080/'~" vue.config.js

npm install

npm run serve
