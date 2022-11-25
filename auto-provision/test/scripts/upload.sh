#!/usr/bin/env bash

set -x
curl -X POST http://localhost:8089/file/upload \
  -F "upload[]=@data1.zip" \
  -F "upload[]=@data2.zip" \
  -H "Content-Type: multipart/form-data"

