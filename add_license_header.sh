#!/bin/bash -e
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

# Search directory, by default current directory
search_dir=${search_dir:-.}

# Read lines from the ignore file into an array
ignore_file="$search_dir/.licignore"
while IFS= read -r pattern; do
  patterns+=( $(echo "$search_dir/$pattern") )
done < "$ignore_file"

function is_ignored() {
  file_path=$1
  # Check if the file path matches any pattern in the array
  for pattern in "${patterns[@]}"; do
    if [[ $file_path == "$pattern"* ]]; then
      return 0  # File path is ignored
    fi
  done
  return 1
}

function add_lic_header() {
  # License file
  license_file="$1"

  # processing file
  file=$2

  # Get license file lines
  lines=$(wc -l "$license_file" | cut -f1 -d ' ')

  # Get the first line of the file
  first_line=$(head -n 1 "$file")

  # Check if the first line starts with a shebang
  if [[ $first_line =~ ^#! ]]; then
      # Skip the shebang line
      ( tail -n +2 "$file" | head -n "$lines" | sed '/^$/d' | diff -q "$license_file" - >/dev/null ) || \
      sed -i "2e cat $license_file" "$file"
  else
      ( head -n "$lines" "$file" | sed '/^$/d'| diff -q "$license_file" - >/dev/null) || \
      sed -i "1e cat $license_file" "$file"
  fi
}

# License header files
lic_header_files=()
for f in license/*; do
  lic_header_files+=("$f")
done

# Loop license header files
for lic in "${lic_header_files[@]}"; do
  extension="*.$(basename $lic)" # file extension name by default 
  if [[ $extension == *"Dockerfile"* ]]; then
    extension="Dockerfile"
  fi

  echo "------------$extension------------------"
  # Find matched files to add license header by extension
  find "$search_dir" -type f -name "$extension" | while read -r file; do
    if is_ignored "$file"; then
      echo "Skip file $file"
    else
      echo "Processing file $file..."
      add_lic_header "$lic" "$file"
    fi
  done
done
