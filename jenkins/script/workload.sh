#! /bin/bash -e

svc_framework_dir="${WORKSPACE}"
mkdir -p "${svc_framework_dir}"
workload_dir="${svc_framework_dir}/validation"
wiki_dir="${svc_framework_dir}/wiki"

prepare_build () {
    timeout="$1"; shift
    commit="$1"; shift
    
    controller_ip=`cat ${WORKSPACE}/pool/cluster.yaml |grep docker_registry | awk '{print $2}'|head -n 1`
    controller_ip=`eval echo $controller_ip`
    registry="$controller_ip"
    #build workload
    mkdir -p "$workload_dir/build"
    if [ "$cumulus_tags" == "" ]
    then
        tag=""
    else
        tag="--tags ${cumulus_tags}"
    fi
    
    svr_info_value="--svrinfo=false"
    if [ "$svrinfo" == "true" ]; then svr_info_value="--svrinfo=true";fi

    emon_value="--emon=false"
    if [ "$emon" == "true" ]; then emon_value="--emon=true --edp_publish --emon_post_process_skip=true";fi

    cumulus_options="${tag} ${svr_info_value} ${emon_value} --owner=sf-post-silicon"
    if [ "$gated" == "true" ]; then cumulus_options="${svr_info_value} ${emon_value}";fi
    if [ "$customer" == "tencent" ] || [ "ali" == "$customer" ]; then cumulus_options="${svr_info_value} --collectd ${tag} ${emon_value}";fi
    delete_runs="\        rm -rf \$tmp_dir/runs/\$run_uri"
    sed -i "/pkb.log/a $delete_runs" $workload_dir/script/validate.sh
    if [ "$gated" == "" ]
    then
	gated="false"
    fi
    pkb_str="\$SCRIPT/cumulus/shell.sh \$image \"\${vmounts[@]}\" \"\${runoptions[@]}\" --name \$run_uri -v \$WORKSPACE:\$WORKSPACE -e WORKSPACE=\$WORKSPACE -e workload=\$workload -e platform=\$platform -e run_on_specific_hw=\$run_on_specific_hw -e run_on_previous_hw=\$run_on_previous_hw -e emon=\$emon -e limited_node_number=\$limited_node_number -e build_id=\$BUILD_ID -e performance=\$performance -e CUMULUS_OPTIONS_EXTRA=\"\$CUMULUS_OPTIONS_EXTRA\" -e specified_node_number=\$specified_node_number -e owner=\$USER  -- python3 ${WORKSPACE}/script/jenkins/script/cluster.py \$CLUSTER_CONFIG \$CUMULUS_CONFIG \$run_uri /tmp/pkb \$CUMULUS_ROOT \"\$CUMULUS_OPTIONS\" $gated"

    s0="s|\$SCRIPT/cumulus/shell.sh .*|$pkb_str|"
    sed -e "$s0" -i $workload_dir/script/cumulus/validate.sh
    # move all cumulus config to temp folder and cp to script/cumulus per jenkins option
    mkdir -p $workload_dir/cumulus
    mv $workload_dir/script/cumulus/cumulus-config.*.yaml $workload_dir/cumulus/

    if [ "true" == "$baremetal" ]
    then
        cp $workload_dir/cumulus/cumulus-config.static.yaml $workload_dir/script/cumulus/cumulus-config.baremetal.yaml
    fi
    if [ "true" == "$gated" ]
    then
        cp $workload_dir/cumulus/cumulus-config.static.yaml $workload_dir/script/cumulus/cumulus-config.cit.yaml
    fi
    if [ "true" == "$snc4" ]
    then
        cp $workload_dir/cumulus/cumulus-config.static.yaml $workload_dir/script/cumulus/cumulus-config.snc4.yaml
    fi
    if [ "true" == "$tdx" ]
    then
        cp $workload_dir/cumulus/cumulus-config.static.yaml $workload_dir/script/cumulus/cumulus-config.tdx.yaml
    fi
    if [ "true" == "$aws" ] || [ "true" == "$gcp" ] || [ "true" == "$azure" ] || [ "true" == "$tencent" ] || [ "true" == "$ali" ] || [ "true" == "$gaudi" ]
    then
        collectd_info=""
        registry="amr-registry-pre.caas.intel.com/sf-cwr-test"
	if [ "true" == "$collectd" ]
	then
            collectd_info="--collectd"
        fi
        cumulus_options="${tag} ${collectd_info} --svrinfo --emon=false --owner=sf-post-silicon"
    fi
    if [ "true" == "$gaudi" ]
    then
        cp $workload_dir/cumulus/cumulus-config.-gaudi.yaml $workload_dir/script/cumulus/cumulus-config.-gaudi.yaml
        cp -rf ~/.aws $workload_dir/script/cumulus/
        if [ $instance ]
        then
            s0="s|vm_count:.*|vm_count: $instance|"
            sed -e "$s0" -i $workload_dir/script/cumulus/cumulus-config.-gaudi.yaml
        fi
    fi
    if [ "true" == "$aws" ]
    then
        config=${aws_machine_type//./-}
        cp $workload_dir/cumulus/cumulus-config.aws.yaml $workload_dir/script/cumulus/cumulus-config.aws-$config.yaml
        cp -rf ~/.aws $workload_dir/script/cumulus/
        if [ $instance ]
        then
            s0="s|vm_count:.*|vm_count: $instance|"
            sed -e "$s0" -i $workload_dir/script/cumulus/cumulus-config.aws-$config.yaml
        fi
        if [ $aws_machine_type ]
        then
            s1="s|machine_type:.*|machine_type: $aws_machine_type|"
            sed -e "$s1" -i $workload_dir/script/cumulus/cumulus-config.aws-$config.yaml
        fi
        if [ $aws_zone ]
        then
            s2="s|zone:.*|zone: $aws_zone|"
            sed -e "$s2" -i $workload_dir/script/cumulus/cumulus-config.aws-$config.yaml
        fi
        if [ "$boot_disk_size" != "" ]
        then
            s3="s|boot_disk_size:.*|boot_disk_size: $boot_disk_size|"
            sed -e "$s3" -i $workload_dir/script/cumulus/cumulus-config.aws-$config.yaml
        fi
    fi
    if [ "true" == "$azure" ]
    then
        config=${azure_machine_type//_/-}
        cp $workload_dir/cumulus/cumulus-config.azure.yaml $workload_dir/script/cumulus/cumulus-config.azure-$config.yaml
        cp -rf ~/.azure $workload_dir/script/cumulus/
        cp -rf ~/.aws $workload_dir/script/cumulus/
        if [ $instance ]
        then
            s0="s|vm_count:.*|vm_count: $instance|"
            sed -e "$s0" -i $workload_dir/script/cumulus/cumulus-config.azure-$config.yaml
        fi
        if [ $azure_machine_type ]
        then
            s1="s|machine_type:.*|machine_type: $azure_machine_type|"
            sed -e "$s1" -i $workload_dir/script/cumulus/cumulus-config.azure-$config.yaml
        fi
        if [ "$boot_disk_size" != "" ]
        then
            s3="s|boot_disk_size:.*|boot_disk_size: $boot_disk_size|"
            sed -e "$s3" -i $workload_dir/script/cumulus/cumulus-config.azure-$config.yaml
        fi
	if [ $azure_zone ]
        then
            s2="s|zone:.*|zone: $azure_zone|"
            sed -e "$s2" -i $workload_dir/script/cumulus/cumulus-config.azure-$config.yaml
        fi
    fi
    if [ "true" == "$gcp" ]
    then
        cp $workload_dir/cumulus/cumulus-config.gcp.yaml $workload_dir/script/cumulus/cumulus-config.gcp-$gcp_machine_type.yaml
        cp -rf ~/.config $workload_dir/script/cumulus/
        cp -rf ~/.aws $workload_dir/script/cumulus/
        if [ $instance ]
        then
            s0="s|vm_count:.*|vm_count: $instance|"
            sed -e "$s0" -i $workload_dir/script/cumulus/cumulus-config.gcp-$gcp_machine_type.yaml
        fi
	if [ $gcp_machine_type ]
        then
            s1="s|machine_type:.*|machine_type: $gcp_machine_type|"
            sed -e "$s1" -i $workload_dir/script/cumulus/cumulus-config.gcp-$gcp_machine_type.yaml
        fi
	if [ $gcp_zone ]
        then
            s2="s|zone:.*|zone: $gcp_zone|"
            sed -e "$s2" -i $workload_dir/script/cumulus/cumulus-config.gcp-$gcp_machine_type.yaml
	    gcp_subnet_region=`echo $gcp_zone|awk -F'-' '{print $1}'`-`echo $gcp_zone|awk -F'-' '{print $2}'`
            s2="s|gce_subnet_region:.*|gce_subnet_region: $gcp_subnet_region|"
            sed -e "$s2" -i $workload_dir/script/cumulus/cumulus-config.gcp-$gcp_machine_type.yaml
        fi
        if [ "$boot_disk_size" != "" ]
        then
            s3="s|gce_boot_disk_size:.*|gce_boot_disk_size: \"$boot_disk_size\"|"
            sed -e "$s3" -i $workload_dir/script/cumulus/cumulus-config.gcp-$gcp_machine_type.yaml
        fi
    fi
    if [ "true" == "$tencent" ]
    then
        config=${tencent_machine_type//./-}
        cp $workload_dir/cumulus/cumulus-config.tencent.yaml $workload_dir/script/cumulus/cumulus-config.tencent-$config.yaml
        cp -rf ~/.tccli $workload_dir/script/cumulus/
        cp -rf ~/.aws $workload_dir/script/cumulus/
        if [ $instance ]
        then
            s0="s|vm_count:.*|vm_count: $instance|"
            sed -e "$s0" -i $workload_dir/script/cumulus/cumulus-config.tencent-$config.yaml
        fi
        if [ $tencent_machine_type ]
        then
            s1="s|machine_type:.*|machine_type: $tencent_machine_type|"
            sed -e "$s1" -i $workload_dir/script/cumulus/cumulus-config.tencent-$config.yaml
        fi
        if [ $tencent_zone ]
        then
            s2="s|zone:.*|zone: $tencent_zone|"
            sed -e "$s2" -i $workload_dir/script/cumulus/cumulus-config.tencent-$config.yaml
        fi
        if [ "$boot_disk_size" != "" ]
        then
            s3="s|tencent_boot_disk_size:.*|tencent_boot_disk_size: \"$boot_disk_size\"|"
            sed -e "$s3" -i $workload_dir/script/cumulus/cumulus-config.tencent-$config.yaml
        fi
    fi
    if [ "true" == "$ali" ]
    then
        config=${ali_machine_type//./-}
        cp $workload_dir/cumulus/cumulus-config.alicloud.yaml $workload_dir/script/cumulus/cumulus-config.alicloud-$config.yaml
        cp -rf ~/.aliyun $workload_dir/script/cumulus/
        cp -rf ~/.aws $workload_dir/script/cumulus/
        if [ $instance ]
        then
            s0="s|vm_count:.*|vm_count: $instance|"
            sed -e "$s0" -i $workload_dir/script/cumulus/cumulus-config.alicloud-$config.yaml
        fi
        if [ $ali_machine_type ]
        then
            s1="s|machine_type:.*|machine_type: $ali_machine_type|"
            sed -e "$s1" -i $workload_dir/script/cumulus/cumulus-config.alicloud-$config.yaml
        fi
        if [ $ali_zone ]
        then
            s2="s|zone:.*|zone: $ali_zone|"
            sed -e "$s2" -i $workload_dir/script/cumulus/cumulus-config.alicloud-$config.yaml
        fi
        if [ "$boot_disk_size" != "" ]
        then
            s3="s|ali_system_disk_size:.*|ali_system_disk_size: $boot_disk_size|"
            sed -e "$s3" -i $workload_dir/script/cumulus/cumulus-config.alicloud-$config.yaml
        fi
    fi
    if [ "SPR" == "$platform" ] && [ "true" == "$vm" ]
    then
        cp $workload_dir/cumulus/cumulus-config.static.yaml $workload_dir/script/cumulus/cumulus-config.vm.yaml
    fi
    if [ "$workload" == "Bitnami-WordPress" ]
    then
        rm -rf $workload_dir/script/cumulus/cumulus-config.*.yaml
        cp $workload_dir/cumulus/cumulus-config.-bitnami.yaml $workload_dir/script/cumulus/cumulus-config.-bitnami.yaml
        cp -rf ~/.azure $workload_dir/script/cumulus/
        latest_image=`az vm image list --all --publisher bitnami|grep Bitnami:wordpress-intel | awk -F\" '{print $4}'`
        s0="s|Bitnami:.*|$latest_image|"
        sed -e "$s0" -i $workload_dir/script/cumulus/cumulus-config.-bitnami.yaml
    fi
    rm -rf "$workload_dir/build" && mkdir -p "$workload_dir/build"
    if [ ! -z $append_cumulus_option ]
    then
        cumulus_options=$cumulus_options" "$append_cumulus_option
    fi
    echo cmake -DPLATFORM=$platform -DRELEASE=:$commit -DACCEPT_LICENSE=ALL -DBACKEND=cumulus -DCUMULUS_OPTIONS="'$cumulus_options'" -DREGISTRY=$registry -DTIMEOUT=$timeout ../
    cd "$workload_dir/build" && cmake -DPLATFORM=$platform -DRELEASE=:$commit -DACCEPT_LICENSE=ALL -DBACKEND=cumulus -DCUMULUS_OPTIONS="'$cumulus_options'" -DREGISTRY=$registry -DTIMEOUT=$timeout ../
}

get_bom () {
    bom=$1; shift
    cd $workload_dir/build
    while read -r line; do
        case "$line" in
        BOM*)
            workload_name=$(echo $line | cut -f3 -d' ')
            title=0
            ;;
        ARG*)
            if [ "$title" -eq 0 ]; then
                used=""
                title=1
            fi
            name=$(echo "$line" | sed 's/ARG *//' | cut -f1 -d=)
            value=$(echo "$line" | sed 's/ARG *//' | cut -f2 -d= | sed 's/"//g')
            eval "$name=$value"
            eval value="$value"

            case "$name" in
            *_REPO)
                name1=${name/_REPO/}
                eval "version=\${${name1}_VER}"
                if [ -z "$version" ]; then version="-"; fi
                if [[ "$used" != *"|$name1:$version|"* ]]; then
                    echo  "$name1 $version" >> $workload_dir/bom/${bom}.txt
                fi
                ;;
            *_IMAGE)
                name1=${name/_IMAGE/}
                eval "version=\${${name1}_VER}"
                if [ -z "$version" ]; then version="-"; fi
                if [[ "$used" != *"|$name1:$version|"* ]]; then
                    echo "$name1 $version" >> $workload_dir/bom/${bom}.txt
                fi
                ;;
            esac
            ;;
        esac
    done < <(make $bom | grep -E '^(BOM|ARG)' 2> /dev/null)
}

run_workload_benchmark () {
    workload=$1; shift
    if [ "main" == "$customer" ]
    then
        workload_build_dir=$workload_dir/build/workload/$workload
    else
        workload_build_dir=$workload_dir/build/workload/customer/$customer/$workload
    fi
    cd $workload_build_dir
    mkdir -p $workload_dir/bom
    for i in `cat CMakeLists.txt  |grep 'add_workload(' | awk -F\" '{print $2}'`
    do
        bom="bom_"${i}
        get_bom $bom
    done

    if [ $parallel_run_case_number ]; then
        test_number=$parallel_run_case_number
    elif [ "true" == "$gcp" ] || [ "true" == "$azure" ] || [ "true" == "$aws" ] || [ "true" == "$tencent" ] || [ "true" == "$ali" ]
    then
        test_number=`ls $workload_dir/script/cumulus/cumulus-config.*|wc -l`
    else
        test_number=5
    fi

    if [ "CDN-NGINX" == "$workload" ] || [ "VPP-FIB" == "$workload" ] || [ "L3FWD-DPDK" == "$workload" ] || [ "CDN-HAProxy" == "$workload" ]
    then
        test_number=1
    fi
    if [ "true" == "$gaudi" ]
    then
        test_number=1
    fi
    if [ "$gated" == "true" ]
    then
        cd "$workload_build_dir" && ctest -R '_gated$' -j$test_number -VV
    else
        if [ -z $filter_case ]
        then
            cd "$workload_build_dir" && TEST_CONFIG=${WORKSPACE}/test_config.yaml ctest -j$test_number -VV
        else
            if [[ $filter_case == !* ]]
            then
                filter_case=`echo $filter_case|awk -F'!' '{print $2}'`
                echo "$workload_dir/build/workload/$workload" ctest -E "$filter_case" -j$test_number -VV
                cd "$workload_build_dir" && TEST_CONFIG=${WORKSPACE}/test_config.yaml ctest -E $filter_case -j$test_number -VV
            else
	        cd "$workload_build_dir" && TEST_CONFIG=${WORKSPACE}/test_config.yaml ctest -R $filter_case -j$test_number -VV
            fi
        fi
    fi
}

create_artifacts () {
    workload=$1; shift
    if [ "main" == "$customer" ]
    then
        build_folder=$workload_dir/build/workload/$workload
    else
        build_folder=$workload_dir/build/workload/customer/$customer/$workload
    fi

    mkdir -p $WORKSPACE/logs/ctest
    mkdir -p $WORKSPACE/result/ctest
    cp -rf $build_folder/Testing/Temporary/* $WORKSPACE/logs/ctest/
    cd $build_folder
    for log in `ls|grep logs`
    do
        if [ -d "$log" ]; then
            #Remove svr-info binary
            rm -rf $build_folder/${log}/svr-info
            #Exclude emon/collectd/svrinfo data if no performance run and user not specified to keep it.
            if [ "$performance" == "false" ] && [ "$keep_emon_collectd_data" == "false" ]
            then
                echo "Exclude emon/collectd/svr_info data"
                for run_id in `ls $build_folder/${log}/runs`
                do
                    rm -rf $build_folder/${log}/runs/$run_id/*-emon
                    rm -rf $build_folder/${log}/runs/$run_id/*-collectd
                    rm -rf $build_folder/${log}/runs/$run_id/*-svrinfo
                done
            fi
            log_name=logs-`echo $log |awk -F'logs-' '{print $2}'`
            cp -rf $build_folder/${log} $WORKSPACE/result/$log_name
            tar czf $log.tar.gz ${log}/
        fi
    done
    latest_test_log=$build_folder/Testing/Temporary/LastTest.log
    if [ ! -f $latest_test_log ]
    then
        latest_test_log=$build_folder/Testing/Temporary/LastTest.log.tmp
    fi
    for test in `cat $latest_test_log|grep Testing |grep test_| awk '{print $3}'`
    do
        test_name=`echo $test | sed -e 's/^test_*//g'`
        kpi_name=kpi_${test_name}
        run_workload_kpi $build_folder $test_name
    done
    cp $build_folder/*.tar.gz $WORKSPACE/logs
    cp -rf $workload_dir/kpi $WORKSPACE/logs
    cp -rf $build_folder/Testing/Temporary/* $WORKSPACE/result/ctest/
    cp -rf $workload_dir/kpi $WORKSPACE/result
    cp -rf $workload_dir/bom $WORKSPACE/result
}

run_workload_kpi () {
    build_folder="$1"; shift
    test_name="$1"; shift

    kpi=kpi_${test_name}

    mkdir -p "$workload_dir/kpi"
    if [ "false" == "$performance" ]
    log_folder=`ls|grep logs|grep $test_name\$`
    then
        ./list-kpi.sh --primary $log_folder |grep ^*| while read i
        do
            echo $i >> "$workload_dir/kpi/$kpi.log"
        done
    else
        itr=1
        ./list-kpi.sh --primary $log_folder |grep ^* | while read i
        do
            echo itr$itr $i >> "$workload_dir/kpi/$kpi.log"
            let itr+=1
        done
        ./list-kpi.sh --primary $log_folder | grep 'med \*' | awk -F'med ' '{print $2}' >> "$workload_dir/kpi/$kpi.log"
    fi
}

while [ "$#" -gt 0  ];do
  case "$1" in
    prepare)
      shift
      timeout=$1
      shift
      commit=$1
      prepare_build $timeout $commit
      shift
      ;;
    benchmark)
        shift
        workload=$1
        shift
        cluster=$1
        run_workload_benchmark $workload
        shift
        ;;
    artifacts)
        shift
        create_artifacts $1
        shift
        ;;
   esac
done

