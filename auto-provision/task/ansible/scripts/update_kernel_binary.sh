#!/usr/bin/env bash
#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

source ../../lib/base_function.sh

system_kernel="$(uname -r)"
echo "The local kernel version is $system_kernel"

generic_version_all=$(apt-cache search linux | grep headers | grep x86 | grep generic | awk -F" " '{print $1}')
lowlatency_version_all=$(apt-cache search linux | grep headers | grep x86 | grep lowlatency | awk -F" " '{print $1}')

generic_version_array=()
lowlatency_version_array=()

gen_index=0
for item in ${generic_version_all}; do
        generic_version_array[$gen_index]=$item
        let "gen_index++"
done

low_index=0
for item in ${lowlatency_version_all}; do
        lowlatency_version_array[low_index]=$item
        let "low_index++"
done

function install_kernel() {

        for kernel_version in $1; do
                contains_str $2 $kernel_version
                res=$(echo $?)
                if [[ $res -eq 0 ]]; then
                        kernel_image="${kernel_version/headers/image}"
                        echo_color green "Start installing new kernel$kernel_image"
                        echo_color green "Start installing new kernel$kernel_version"
                        sudo apt-get install "${kernel_image}" -y
                        sudo apt-get install "${kernel_version}" -y
                        break
                else
                        :
                fi
        done

}

function display_type_page() {

        printLine
        echo_color green "Please select the kernel version type you want to install:"
        echo_color green "1: generic"
        echo_color green "2: lowlatency"
        printLine

}

function display_version_page() {

        if [ "$type_number" == "1" ]; then

                printLine
                version_array="$generic_version_array"
                for number in "${!generic_version_array[@]}"; do
                        if [ $(($number % 2)) -eq 0 ]; then
                                next=$(expr $number + 1)
                                echo_color green "$number : ${generic_version_array[$number]} || $next :  \
                                         ${generic_version_array[$next]}"
                        fi
                done
                printLine
        elif [ "$type_number" == "2" ]; then

                printLine
                version_array=$lowlatency_version_array
                for number in "${!lowlatency_version_array[@]}"; do
                        if [ $(($number % 2)) -eq 0 ]; then
                                next=$(expr $number + 1)
                                echo_color green "$number :  ${lowlatency_version_array[$number]} || $next :  \
                                         ${lowlatency_version_array[$next]}"
                        fi
                done
                printLine
        else
                echo_color red "The type you selected does not exist......"
                exit 1
        fi

}

function run() {

        if [ "$1" == "generic" ]; then
                echo_color green "install generic kernel......"
                install_kernel "$generic_version_all" "${generic_version_array[$2]}"
        elif [ "$1" == "lowlatency" ]; then
                echo_color green "install lowlatency kernel......"
                install_kernel "$lowlatency_version_all" "${generic_version_array[$2]}"
        else
                echo_color red "The kernel version type you selected does not exist......"
                exit 1
        fi
}

# start
display_type_page
read -p "Please input the number: " type_number
if [ "$type_number" == "1" ]; then
        echo_color green "You selected generic kernel"
        display_version_page $type_number
        read -p "Please input the number:" version_number
        #run "generic" ${generic_version_array["$version_number"]}
        run "generic" $version_number
elif [ "$type_number" == "2" ]; then
        echo_color green "You selected lowlatency kernel"
        display_version_page $type_number
        read -p "Please input the number: " version_number
        #run "lowlatency" ${lowlatency_version_array[$version_number]}
        run "lowlatency" $version_number
else
        echo_color red "The kernel version type you selected does not exist......"
        exit 1
fi

# config grub
printLine
if [ !-d "/boot/efi" ]; then
        sudo grub-editenv /boot/grub/grubenv create
else
        sudo grub-editenv /boot/efi/EFI/ubuntu/grubenv create
fi
sudo update-grub
printLine
sudo reboot

<<'COMMENT'

kernel_type="generic"
generic_version_all=$(apt-cache search linux | grep headers | grep x86 | grep generic | awk -F" " '{print $1}')
#the_version=$($generic_version_all | awk -F"-" '{print $3"-"$4}')
the_version="5.8.0-63"
grub_advanced=$(grep submenu /boot/grub/grub.cfg |   awk -F"'" '{print $4}') 
uuid=$(echo $grub_advanced | awk -F"advanced" '{print $2}')
GRUB_DEFAULT="$grub_advanced>gnulinux-$the_version-$kernel_type-recovery$uuid"
echo $GRUB_DEFAULT
#sed -i "s/^/" grub 

COMMENT
