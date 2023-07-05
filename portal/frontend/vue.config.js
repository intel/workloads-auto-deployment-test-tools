/*
Apache v2 license
Copyright (C) 2023 Intel Corporation
SPDX-License-Identifier: Apache-2.0
*/
const BundleTracker = require('webpack-bundle-tracker')

module.exports = {
  // on Windows you might want to set publicPath: "http://127.0.0.1:8080/"
  // Note: You don't need to change this IP in development since start_dev.sh
  // will change it automatically
  publicPath: '/static',
  outputDir: './dist/',

  chainWebpack: config => {
    config
      .plugin('BundleTracker')
      .use(BundleTracker, [{ filename: './webpack-stats.json' }])

    config.output
      .filename('bundle.js')

    config.optimization
        	.splitChunks(false)

    config.resolve.alias
      .set('__STATIC__', 'static')

    config.devServer
    // the first 3 lines of the following code have been added to the configuration
      // .host('10.166.33.34')
      // .port(8080)
      .https(true)
      .historyApiFallback(true)
      .headers({ 'Access-Control-Allow-Origin': ['\*'] })
  },
  devServer: {
    host: "0.0.0.0",
    port:8080,
    allowedHosts: "all",
    liveReload: true,
    hot: "only"
  },

  // uncomment before executing 'npm run build'
  css: {
    extract: {
      filename: 'bundle.css',
      chunkFilename: 'bundle.css'
    }
  }

}
