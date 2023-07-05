#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
echo '/dev/vdb1 /mnt/vdb1 ext4 defaults 0 0'  >> /etc/fstab
parted /dev/vdb mklabel gpt Yes
parted /dev/vdb  mkpart  primary 0G 10G
mkfs.ext4 /dev/vdb1
mount /dev/vdb1 /mnt/vdb1/
