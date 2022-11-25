#!/usr/bin/env bash


#Get vitual disk information
lsblk |grep vd[a-z] > diskinfo


#Filter out disks without partitions
for i in {b..z}; do
	disk_part_num=$(grep "vd$i" /root/diskinfo | wc -l)

	#If the statistical number is 1, so it means that there is only disk and no part
	if [ $disk_part_num -eq 1 ];then
		echo vd$i
		echo "start to mount disk"

		#If the directory is not exist, create it.
		if [ ! -f "/mnt/vd${i}1" ];then
			mkdir /mnt/vd${i}1
		fi

		#Format disk
		parted -a opt -s /dev/vd$i mklabel gpt

		#Partition disk
		parted /dev/vd$i mkpart vd$i_part1 ext4 0% 100%

		#Format disk by mkfs
		yes|mkfs -t ext4 /dev/vd${i}1

		#Mount
		mount /dev/vd${i}1 /mnt/vd${i}1/
	fi
done
