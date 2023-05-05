#! /bin/bash -e

svc_framework_dir="${WORKSPACE}"
mkdir -p "${svc_framework_dir}"
workload_dir="${svc_framework_dir}/validation"
wiki_dir="${svc_framework_dir}/wiki"

prepare_build_terraform () {
    timeout="$1"; shift
    commit="$1"; shift
    
    controller_ip=`cat ${WORKSPACE}/pool/cluster.yaml |grep docker_registry | awk '{print $2}'|head -n 1 | tr -d '\r'`
    controller_ip=`eval echo $controller_ip`
    registry="$controller_ip"
    #use test_config.yaml from workoad folder
    if [ "$workload_test_config_yaml" != "" ]
    then
        test_config_path=`find ${workload_dir}/workload/${workload} -name ${workload_test_config_yaml}`
	if [ -f ${test_config_path} ]
	then
            cp -f ${test_config_path} ${WORKSPACE}/test_config.yaml
	else
	    echo "test configuration file doesn't exist, use default configuration."
	fi
    fi

    #build workload
    mkdir -p "$workload_dir/build"
    
    svr_info_value="--svrinfo"
    if [ "$svrinfo" == "false" ]; then svr_info_value="--svrinfo=false";fi
    gprofiler_value=""
    if [ "$gprofiler" == "true" ]; then gprofiler_value="--gprofiler";fi
    emon_value=""
    if [ "$emon" == "true" ]; then emon_value="--emon --noemon_post_processing";fi
    
    if [ "$cumulus_tags" == "" ]
    then
        tag=""
    else
        tag="--tags=${cumulus_tags}"
    fi

    collectd_info=""
    if [ "true" == "$collectd" ]
    then
        collectd_info="--collectd"
    fi
    # Need a default owner
    intel_publish_info="--owner=vaas"
    if [ "true" == "$intel_publish" ]
    then
        intel_publish_info="--intel_publish --intel_publisher_mongodb_name=services-framework --owner=sf-post-silicon"
    fi
    terraform_options="${tag} ${collectd_info} ${svr_info_value} ${emon_value} ${gprofiler_value} ${intel_publish_info}"
    if [ "$gated" == "true" ]; then terraform_options="--svrinfo=false ${emon_value} --owner=sf-post-silicon";fi
    if [ "$customer" == "tencent" ] || [ "ali" == "$customer" ]; then terraform_options="${svr_info_value} ${collectd_info} ${tag} ${emon_value} --owner=sf-post-silicon";fi

    if [ "$gated" == "" ] 
    then
	gated="false"
    fi

    network_option=""
    if [ "false" == "$default_docker_network" ]
    then
	network_option="--network non_default_bridge"
    fi
    st="\        st_options=\"\${st_options[@]}\""
    sed -i "/terraform\/shell.sh/i $st" $workload_dir/script/terraform/validate.sh
    run_str="\        run_uri=\$(cat \/proc\/sys\/kernel\/random\/uuid | cut -f5 -d-)"
    sed -i "/terraform\/shell.sh/i $run_str" $workload_dir/script/terraform/validate.sh

    pkb_str="\"\$PROJECTROOT\"/script/terraform/shell.sh \${csp:-static} \"\${dk_options[@]}\" $network_option --name \$run_uri -v \$WORKSPACE:\$WORKSPACE -e debug=\$debug -e WORKSPACE=\$WORKSPACE -e workload=\$workload -e platform=\$platform -e run_on_specific_hw=\$run_on_specific_hw -e run_on_previous_hw=\$run_on_previous_hw -e emon=\$emon -e limited_node_number=\$limited_node_number -e build_id=\$BUILD_ID -e performance=\$performance  -e CTESTSH_OPTIONS=\"\$CTESTSH_OPTIONS\" -e st_options=\"\$st_options\" -e specified_node_number=\$specified_node_number -e owner=\$USER -e backend=\$backend -- python3 ${WORKSPACE}/script/jenkins/script/cluster.py \$CLUSTER_CONFIG \$TERRAFORM_CONFIG \$run_uri /tmp/pkb \"\$TERRAFORM_OPTIONS\" $gated "

    s0="s|\"\$PROJECTROOT\"/script/terraform/shell.sh .*|$pkb_str|"
    sed -e "$s0" -i $workload_dir/script/terraform/validate.sh
    
    if [ "true" == "$baremetal" ] || [ "true" == "$gated" ]
    then
        # add variable json in terraform apply
        tf_var="\  terraform plan -var-file=variable-values.json"
        s0="s|terraform plan (.*\&?)|$tf_var \1|"
        sed -re "$s0" -i $workload_dir/script/terraform/script/start.sh
        tf_destroy="\    TF_LOG=ERROR terraform destroy -var-file=variable-values.json -auto-approve -input=false -no-color -parallelism=1"
        s0="s|.* terraform destroy .*|$tf_destroy|"
        sed -e "$s0" -i $workload_dir/script/terraform/script/start.sh
    fi

    # move all terraform config to temp folder and cp to script/terraform per jenkins option
    mkdir -p $workload_dir/terraform
    mv $workload_dir/script/terraform/terraform-config.*.tf $workload_dir/terraform/
    k8s_enable_registry="\    k8s_enable_registry : false,"
    wl_enable_reboot="\    wl_enable_reboot : false,"
    cloud_overwrite_setting=()

    if [ "true" == "$baremetal" ]
    then
        if [ "$workload_test_config_yaml" != "" ]
        then
            config=${workload_test_config_yaml//_/-}
            config=${config//.yaml/}
        else
            config=default
        fi
        cp $workload_dir/terraform/terraform-config.static.tf $workload_dir/script/terraform/terraform-config.baremetal-$config.tf
        sed -i "/.* var.intel_publisher_sut_metadata.*/a $k8s_enable_registry" $workload_dir/script/terraform/terraform-config.baremetal-$config.tf
	sed -i "/.* var.intel_publisher_sut_metadata.*/a $wl_enable_reboot" $workload_dir/script/terraform/terraform-config.baremetal-$config.tf
    fi
    if [ "true" == "$gated" ]
    then
        cp $workload_dir/terraform/terraform-config.static.tf $workload_dir/script/terraform/terraform-config.cit.tf
        sed -i "/.* var.intel_publisher_sut_metadata.*/a $k8s_enable_registry" $workload_dir/script/terraform/terraform-config.cit.tf
	sed -i "/.* var.intel_publisher_sut_metadata.*/a $wl_enable_reboot" $workload_dir/script/terraform/terraform-config.cit.tf
    fi
    if [ "true" == "$snc4" ]
    then
        cp $workload_dir/terraform/terraform-config.static.tf $workload_dir/script/terraform/terraform-config.snc4.tf
    fi
    if [ "true" == "$tdx" ]
    then
        cp $workload_dir/terraform/terraform-config.static.tf $workload_dir/script/terraform/terraform-config.tdx.tf
    fi
    if [ "true" == "$aws" ] || [ "true" == "$gcp" ] || [ "true" == "$azure" ] || [ "true" == "$tencent" ] || [ "true" == "$ali" ] || [ "-inf" == "$specific_sut" ] || [ "-gaudi" == "$specific_sut" ] || [ "-t4" == "$specific_sut" ]
    then
        collectd_info=""
	cloud_overwrite_setting+=(--set SPOT_INSTANCE=false)
        if [ "true" == "$collectd" ]
        then
            collectd_info="--collectd"
        fi
        intel_publish_info=""
	if [ "true" == "$intel_publish" ]
        then
            intel_publish_info="--intel_publish --intel_publisher_mongodb_name=services-framework --owner=sf-post-silicon "
        fi
        terraform_options="${tag} ${collectd_info} --skopeo_insecure_registries=${registry} --svrinfo ${emon_value} ${intel_publish_info}"
        #Temporarily added '--docker-run' to -inf SUT as k8s run doesn't supported now.
        if [ "-inf" == "$specific_sut" ]
        then
            terraform_options=$terraform_options" --docker-run"
        fi
    fi
    if [ "-gaudi" == "$specific_sut" ]
    then
        cp $workload_dir/terraform/terraform-config.-gaudi.tf $workload_dir/script/terraform/terraform-config.-gaudi.tf
        cp -rf ~/.aws $workload_dir/script/csp/
    fi
    if [ "-inf" == "$specific_sut" ]
    then
        cp $workload_dir/terraform/terraform-config.-inf.tf $workload_dir/script/terraform/terraform-config.-inf.tf
        cp -rf ~/.aws $workload_dir/script/csp/
    fi
    if [ "-t4" == "$specific_sut" ]
    then
        cp $workload_dir/terraform/terraform-config.-t4.tf $workload_dir/script/terraform/terraform-config.-t4.tf
        cp -rf ~/.aws $workload_dir/script/csp/
    fi
    make_needed=false
    make_sut_option=""
    #mcnat only
    if [[ $specific_sut == *"mcnat"* ]]
    then
        make_needed=true
        aws="false"
        gcp="false"
        azure="false"
        IFS=" "
        make_sut_option=()
        terraform_options=$(echo $terraform_options | sed 's/--owner=\S*/--owner=mcnat/')
        read -r -a array <<< "$specific_sut"
        for i in "${!array[@]}"; do
            if [ "-mcnat-aws" == "${array[$i]}" ]
            then
                config=${aws_machine_type//./-}
                cp $workload_dir/terraform/terraform-config.-mcnat-aws.tf $workload_dir/script/terraform/terraform-config.-mcnat-aws-$config.tf
                cp -rf ~/.aws $workload_dir/script/csp/
                sed -i "/ SUT /s/-mcnat-aws/-mcnat-aws-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
                [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/-mcnat-aws/-mcnat-aws-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
                if [ $aws_machine_type ] ; then cloud_overwrite_setting+=(--set AWS_WORKER_INSTANCE_TYPE=$aws_machine_type --set AWS_MACHINE_TYPE=$aws_machine_type); fi
                if [ $aws_zone ] ; then cloud_overwrite_setting+=(--set AWS_ZONE=$aws_zone --set AWS_REGION=${aws_zone:0:-1}); fi
                sed -i "s/region = .*/region = ${aws_zone:0:-1}/g" $workload_dir/script/csp/.aws/config
                make_sut_option+=(-mcnat-aws-$config)
            elif [ "-mcnat-gcp" == "${array[$i]}" ]
            then
                config=${gcp_machine_type}
                cp $workload_dir/terraform/terraform-config.-mcnat-gcp.tf $workload_dir/script/terraform/terraform-config.-mcnat-gcp-$gcp_machine_type.tf
                cp -rf ~/.config $workload_dir/script/csp/
                sed -i "s/region = .*/region = ${gcp_zone}/g" $workload_dir/script/csp/.config/gcloud/configurations/config_default
                sed -i "s/zone = .*/zone = ${gcp_zone:0:-2}/g" $workload_dir/script/csp/.config/gcloud/configurations/config_default
                sed -i "/ SUT /s/-mcnat-gcp/-mcnat-gcp-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
                [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/-mcnat-gcp/-mcnat-gcp-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
                if [ $gcp_machine_type ] ; then cloud_overwrite_setting+=(--set GCP_WORKER_INSTANCE_TYPE=$gcp_machine_type --set GCP_MACHINE_TYPE=$gcp_machine_type); fi
                if [ $gcp_zone ] ; then cloud_overwrite_setting+=(--set GCP_ZONE=$gcp_zone --set GCP_REGION=${gcp_zone:0:-2}); fi
                make_sut_option+=(-mcnat-gcp-$gcp_machine_type)
            else
                config=${azure_machine_type//_/-}
                cp $workload_dir/terraform/terraform-config.-mcnat-azure.tf $workload_dir/script/terraform/terraform-config.-mcnat-azure-$config.tf
                cp -rf ~/.azure $workload_dir/script/csp/
                sed -i "/ SUT /s/-mcnat-azure/-mcnat-azure-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
                [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/-mcnat-azure/-mcnat-azure-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
                if [ $azure_machine_type ] ; then cloud_overwrite_setting+=(--set AZURE_WORKER_INSTANCE_TYPE=$azure_machine_type --set AZURE_MACHINE_TYPE=$azure_machine_type); fi
                if [ $azure_zone ] ; then cloud_overwrite_setting+=(--set AZURE_ZONE=$azure_zone --set AZURE_REGION=${azure_zone:0:-2}); fi
                make_sut_option+=(-mcnat-azure-$config)
            fi
        done
        make_sut_option="-DTERRAFORM_SUT='${make_sut_option[@]}'" 
    fi
    #non-mcnat 
    if [ "true" == "$aws" ]
    then
        config=${aws_machine_type//./-}
        cp $workload_dir/terraform/terraform-config.aws.tf $workload_dir/script/terraform/terraform-config.aws-$config.tf
        cp -rf ~/.aws $workload_dir/script/csp/
        sed -i "/ SUT /s/aws/aws-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
        [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/aws/aws-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
        k8s_registry_storage="s|# k8s_registry_storage:.*|k8s_registry_storage: \"aws\",|"
        k8s_registry_aws_storage_bucket="s|# k8s_registry_aws_storage_bucket:.*|k8s_registry_aws_storage_bucket: \"cumulus\",|"
        k8s_registry_aws_storage_region="s|# k8s_registry_aws_storage_region:.*|k8s_registry_aws_storage_region: \"us-east-2\",|"
        sed -e "$k8s_registry_storage" -i $workload_dir/script/terraform/terraform-config.aws-$config.tf
        sed -e "$k8s_registry_aws_storage_bucket" -i $workload_dir/script/terraform/terraform-config.aws-$config.tf
        sed -e "$k8s_registry_aws_storage_region" -i $workload_dir/script/terraform/terraform-config.aws-$config.tf
	if [ $aws_machine_type ] ; then cloud_overwrite_setting+=(--set AWS_WORKER_INSTANCE_TYPE=$aws_machine_type --set AWS_MACHINE_TYPE=$aws_machine_type); fi
        if [ $aws_zone ] ; then cloud_overwrite_setting+=(--set AWS_ZONE=$aws_zone --set AWS_REGION=${aws_zone:0:-1}); fi
        if [ $aws_client_machine_type ] ; then cloud_overwrite_setting+=(--set AWS_CLIENT_INSTANCE_TYPE=$aws_client_machine_type); fi
	if [ $boot_disk_size ] ; then cloud_overwrite_setting+=(--set AWS_WORKER_OS_DISK_SIZE=$boot_disk_size); fi
    fi
    if [ "true" == "$azure" ]
    then
        config=${azure_machine_type//_/-}
	sed -i "/ SUT /s/azure/azure-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
        [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/azure/azure-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
        cp $workload_dir/terraform/terraform-config.azure.tf $workload_dir/script/terraform/terraform-config.azure-$config.tf
        cp -rf ~/.azure $workload_dir/script/csp/
	if [ $azure_machine_type ] ; then cloud_overwrite_setting+=(--set AZURE_WORKER_INSTANCE_TYPE=$azure_machine_type --set AZURE_MACHINE_TYPE=$azure_machine_type); fi
        if [ $azure_zone ] ; then cloud_overwrite_setting+=(--set AZURE_ZONE=$azure_zone --set AZURE_REGION=${azure_zone:0:-2}); fi
        if [ $azure_client_machine_type ] ; then cloud_overwrite_setting+=(--set AZURE_CLIENT_INSTANCE_TYPE=$azure_client_machine_type); fi
	if [ $boot_disk_size ] ; then cloud_overwrite_setting+=(--set AZURE_WORKER_OS_DISK_SIZE=$boot_disk_size); fi
    fi
    if [ "true" == "$gcp" ]
    then
        cp $workload_dir/terraform/terraform-config.gcp.tf $workload_dir/script/terraform/terraform-config.gcp-$gcp_machine_type.tf
        config=${gcp_machine_type}
        sed -i "/ SUT /s/gcp/gcp-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
        [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/gcp/gcp-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
        cp -rf ~/.config $workload_dir/script/csp/
	if [ $gcp_machine_type ] ; then cloud_overwrite_setting+=(--set GCP_WORKER_INSTANCE_TYPE=$gcp_machine_type --set GCP_MACHINE_TYPE=$gcp_machine_type); fi
        if [ $gcp_zone ] ; then cloud_overwrite_setting+=(--set GCP_ZONE=$gcp_zone --set GCP_REGION=${gcp_zone:0:-2}); fi
        if [ $gcp_client_machine_type ] ; then cloud_overwrite_setting+=(--set GCP_CLIENT_INSTANCE_TYPE=$gcp_client_machine_type); fi
	if [ $boot_disk_size ] ; then cloud_overwrite_setting+=(--set GCP_WORKER_OS_DISK_SIZE=$boot_disk_size); fi
    fi
    if [ "true" == "$vsphere" ]
    then
        cp $workload_dir/terraform/terraform-config.vsphere.tf $workload_dir/script/terraform/terraform-config.vsphere-$vsphere_machine_type.tf
        config=${vsphere_machine_type}
        sed -i "/ SUT /s/vsphere/vsphere-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
        [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/vsphere/vsphere-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
        cp -rf ~/.vsphere $workload_dir/script/csp/
	if [ $vsphere_machine_type ] ; then cloud_overwrite_setting+=(--set VSPHERE_WORKER_INSTANCE_TYPE=$vsphere_machine_type --set VSPHERE_MACHINE_TYPE=$vsphere_machine_type); fi
        if [ $vsphere_client_machine_type ] ; then cloud_overwrite_setting+=(--set VSPHERE_CLIENT_INSTANCE_TYPE=$vsphere_client_machine_type); fi
    fi
    if [ "true" == "$tencent" ]
    then
        config=${tencent_machine_type//./-}
        sed -i "/ SUT /s/tencent/tencent-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
        [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/tencent/tencent-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
        cp $workload_dir/terraform/terraform-config.tencent.tf $workload_dir/script/terraform/terraform-config.tencent-$config.tf
        cp -rf ~/.tccli $workload_dir/script/csp/
	if [ $tencent_machine_type ] ; then cloud_overwrite_setting+=(--set TENCENT_WORKER_INSTANCE_TYPE=$tencent_machine_type --set TENCENT_MACHINE_TYPE=$tencent_machine_type); fi
        if [ $tencent_zone ] ; then cloud_overwrite_setting+=(--set TENCENT_ZONE=$tencent_zone --set TENCENT_REGION=${tencent_zone:0:-2}); fi
        if [ $tencent_client_machine_type ] ; then cloud_overwrite_setting+=(--set TENCENT_CLIENT_INSTANCE_TYPE=$tencent_client_machine_type); fi
        if [ $tencent_controller_machine_type ] ; then cloud_overwrite_setting+=(--set TENCENT_CONTROLLER_INSTANCE_TYPE=$tencent_controller_machine_type); fi
	if [ $boot_disk_size ] ; then cloud_overwrite_setting+=(--set TENCENT_WORKER_OS_DISK_SIZE=$boot_disk_size); fi
    fi
    if [ "true" == "$ali" ]
    then
        config=${ali_machine_type//./-}
        sed -i "/ SUT /s/alicloud/alicloud-$config/g" $workload_dir/workload/$workload/CMakeLists.txt
        [ -d $workload_dir/workload/$workload/cmake/ ] && sed -i "/ SUT /s/alicloud/alicloud-$config/g" $workload_dir/workload/$workload/cmake/*.cmake
        cp $workload_dir/terraform/terraform-config.alicloud.tf $workload_dir/script/terraform/terraform-config.alicloud-$config.tf
        cp -rf ~/.aliyun $workload_dir/script/csp/
	if [ $ali_machine_type ] ; then cloud_overwrite_setting+=(--set ALICLOUD_WORKER_INSTANCE_TYPE=$ali_machine_type --set ALICLOUD_MACHINE_TYPE=$ali_machine_type); fi
        if [ $ali_zone ] ; then cloud_overwrite_setting+=(--set ALICLOUD_ZONE=$ali_zone --set ALICLOUD_REGION=${ali_zone:0:-2}); fi
        if [ $ali_client_machine_type ] ; then cloud_overwrite_setting+=(--set ALICLOUD_CLIENT_INSTANCE_TYPE=$ali_client_machine_type); fi
        if [ $ali_controller_machine_type ] ; then cloud_overwrite_setting+=(--set ALICLOUD_CONTROLLER_INSTANCE_TYPE=$ali_controller_machine_type); fi
	if [ $boot_disk_size ] ; then cloud_overwrite_setting+=(--set ALICLOUD_WORKER_OS_DISK_SIZE=$boot_disk_size); fi
    
    fi
    if [ "SPR" == "$platform" ] && [ "true" == "$vm" ]
    then
        if [ "$workload_test_config_yaml" != "" ]
        then
            config=${workload_test_config_yaml//_/-}
            config=${config//.yaml/}
        else
            config=default
        fi
        cp $workload_dir/terraform/terraform-config.static.tf $workload_dir/script/terraform/terraform-config.vm-$config.tf
    fi

    rm -rf "$workload_dir/build" && mkdir -p "$workload_dir/build"
    if [ ! -z "$append_option" ]
    then
        terraform_options=$terraform_options" "$append_option
    fi
    if [ "true" == "$external" ]
    then
        commit="ext_"$commit
    fi
    echo ${cloud_overwrite_setting[@]} > ${WORKSPACE}/cloud_setting
    echo "cloud setting is ${cloud_overwrite_setting[@]}"
    echo cmake -DPLATFORM=$platform $make_sut_option -DRELEASE=:$commit -DACCEPT_LICENSE=ALL -DBACKEND=terraform -DBENCHMARK='' -DTERRAFORM_OPTIONS="'$terraform_options'" -DREGISTRY=$registry -DTIMEOUT=$timeout ../
    cd "$workload_dir/build" && cmake -DPLATFORM=$platform "$make_sut_option" -DRELEASE=:$commit -DACCEPT_LICENSE=ALL -DBACKEND=terraform -DBENCHMARK='' -DTERRAFORM_OPTIONS="'$terraform_options'" -DREGISTRY=$registry -DTIMEOUT=$timeout ../
    if [ $make_needed == "true" ]
    then
        cd $workload_dir/build/workload/$workload && make
    fi
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

ctest_reuse_sut()
{
    if [ -z $1 ]
    then
        filter=''
    else
        filter=$1; shift
    fi

    if [ -z $1 ]
    then
        exclude=''
    else
        exclude=$1; shift
    fi

    cloudlist=()
    [ "true" == "$aws" ] && cloudlist+=("aws")
    [ "true" == "$gcp" ] && cloudlist+=("gcp")
    [ "true" == "$azure" ] && cloudlist+=("azure")
    [ "true" == "$tencent" ] && cloudlist+=("tencent")
    [ "true" == "$ali" ] && cloudlist+=("alicloud")

    for cloud in ${cloudlist[@]}
    do
        if [ -z $filter ] && [ -z $exclude ]
        then
            caselist=$(ctest -N | grep -i $cloud | grep -vi _gated | awk '{print $NF}')
        elif [ ! -z $filter ] && [ -z $exclude ]
        then
            caselist=$(ctest -N | grep -i $cloud | grep -vi _gated | grep -E $filter | awk '{print $NF}')
        elif [ -z $filter ] && [ ! -z $exclude ]
        then
            caselist=$(ctest -N | grep -i $cloud | grep -vi _gated | grep -Ev $exclude | awk '{print $NF}')
        else
            caselist=$(ctest -N | grep -i $cloud | grep -vi _gated | grep -E $filter | grep -Ev $exclude | awk '{print $NF}')
        fi
	echo 'Test List: '$caselist
		
	declare -i i=0
	for case in $caselist
	do
	    [ $i -eq 0 ] && ./ctest.sh -R ${case:5}$ --test-config=${WORKSPACE}/test_config.yaml --prepare-sut -V && i+=1 && firstcase=${case:5}
	    [ $i -gt 0 ] && ([ -d sut-logs-${case:5} ] ||cp -rp sut-logs-${firstcase} sut-logs-${case:5}) && ./ctest.sh -R ${case:5}$ --test-config=${WORKSPACE}/test_config.yaml --reuse-sut -V
	    cp -rp Testing Testing_${case:5}
	done
	./ctest.sh -R ${case:5}$ --test-config=${WORKSPACE}/test_config.yaml --cleanup-sut -V
	
	[ -f Testing/Temporary/LastTest.log ] && rm -f Testing/Temporary/LastTest.log && cat $(find Testing_* -name LastTest.log ) >> Testing/Temporary/LastTest.log
	[ -f Testing/Temporary/LastTestsFailed.log ] && rm -f Testing/Temporary/LastTestsFailed.log && cat $(find Testing_* -name LastTestsFailed.log ) >> Testing/Temporary/LastTestsFailed.log

	for sutdir in $(ls -d sut-logs-*)
	do
	    [[ $sutdir == *$firstcase* ]] || rm -rf $sutdir
	done
	
	for dir in $(date "+%m%d")-*-logs-*
	do
	    [ -d ${dir:12} ] && rm -rf ${dir:12}
	    mv $dir ${dir:12}
	done
    done
}

run_workload_benchmark () { 
    workload=$1; shift
    if [ "main" == "$customer" ]
    then
        workload_build_dir=$workload_dir/build/workload/$workload
    else
        workload_build_dir=$workload_dir/build/workload/customer/$customer/$workload
    fi
    if [ -f ${WORKSPACE}/cloud_setting ]
    then
        CLOUD_OVERWRITE_SETTING=$(cat ${WORKSPACE}/cloud_setting)
    else
        CLOUD_OVERWRITE_SETTING=""
    fi
    echo "ctest cloud setting is ${CLOUD_OVERWRITE_SETTING}"
    cd $workload_build_dir
    mkdir -p $workload_dir/bom
    for i in `cat CMakeLists.txt  |grep 'add_workload(' | awk -F\" '{print $2}'`
    do
        bom="bom_"${i}
        get_bom $bom
    done
    if [ "true" == "$performance" ] ; then use_ctest_script=true; fi
    if [ "true" == "$gcp" ] || [ "true" == "$azure" ] || [ "true" == "$aws" ] || [ "true" == "$tencent" ] || [ "true" == "$ali" ] || [ "true" == "$vsphere" ]
	then
	    use_ctest_script=true
	fi
    if [ $parallel_run_case_number ]; then
        test_number=$parallel_run_case_number
    elif [ "true" == "$gcp" ] || [ "true" == "$azure" ] || [ "true" == "$aws" ] || [ "true" == "$tencent" ] || [ "true" == "$ali" ]
    then
        test_number=`ls $workload_dir/script/terraform/terraform-config.*|wc -l`
    else
        test_number=5
    fi

    if [ "CDN-NGINX" == "$workload" ] || [ "VPP-FIB" == "$workload" ] || [ "L3FWD-DPDK" == "$workload" ] || [ "CDN-HAProxy" == "$workload" ]
    then
        test_number=1
    fi
    if [ "-inf" == "$specific_sut" ] || [ "-gaudi" == "$specific_sut" ]|| [ "-t4" == "$specific_sut" ]
    then
        test_number=1
    fi
    if [ "$gated" == "true" ]
    then
        gated_case=`cd "$workload_build_dir" && ctest -N | grep gated | wc -l`
	if [ "$gated_case" != 0 ]
	then
	    cd "$workload_build_dir" && ctest -R '_gated$' -j$test_number -VV
	else
	    echo "WARNING: There is no gated case for this Workload, need to check"
	    exit 1
	fi
    else
        if [ -z $filter_case ] && [ -z $exclude_case ]
        then
            if [ "true" == "$use_ctest_script" ]
            then
                cd $workload_build_dir && ./ctest.sh ${CLOUD_OVERWRITE_SETTING} --run=${iteration} --test-config=${WORKSPACE}/test_config.yaml -E '_gated$' -VV 
            elif [ "true" == "$share_sut" ]
            then
                cd "$workload_build_dir" && ctest_reuse_sut $filter_case $exclude_case
            else
                echo "TEST_CONFIG=${WORKSPACE}/test_config.yaml ctest -E '_gated$' -j$test_number -VV"
                cd $workload_build_dir && TEST_CONFIG=${WORKSPACE}/test_config.yaml ctest -E '_gated$' -j$test_number -VV
            fi
        elif [ ! -z $filter_case ] && [ -z $exclude_case ]
        then
            if [ "true" == "$use_ctest_script" ]
            then
                cd $workload_build_dir && ./ctest.sh ${CLOUD_OVERWRITE_SETTING} --run=${iteration} --test-config=${WORKSPACE}/test_config.yaml -E "_gated$" -R $filter_case -VV
            elif [ "true" == "$share_sut" ]
            then
                cd "$workload_build_dir" && ctest_reuse_sut $filter_case $exclude_case
            else
                echo "$workload_dir/build/workload/$workload" ctest -E "_gated$" -R $filter_case -j$test_number -VV
                cd "$workload_build_dir" && TEST_CONFIG=${WORKSPACE}/test_config.yaml ctest -E "_gated$" -R $filter_case -j$test_number -VV
            fi
        elif [ -z $filter_case ] && [ ! -z $exclude_case ]
        then
            if [ "true" == "$use_ctest_script" ]
            then
                cd $workload_build_dir && ./ctest.sh ${CLOUD_OVERWRITE_SETTING} --run=${iteration} --test-config=${WORKSPACE}/test_config.yaml -E "_gated$|$exclude_case" -VV
            elif [ "true" == "$share_sut" ]
            then
                cd "$workload_build_dir" && ctest_reuse_sut $filter_case $exclude_case
            else
                echo "$workload_dir/build/workload/$workload" ctest -E "_gated$|$exclude_case" -j$test_number -VV
                cd "$workload_build_dir" && TEST_CONFIG=${WORKSPACE}/test_config.yaml ctest -E "_gated$|$exclude_case" -j$test_number -VV	
            fi
        else
            if [ "true" == "$use_ctest_script" ]
            then
                cd $workload_build_dir && ./ctest.sh ${CLOUD_OVERWRITE_SETTING} -E "_gated$|$exclude_case" -R $filter_case --run=${iteration} --test-config=${WORKSPACE}/test_config.yaml -VV
            elif [ "true" == "$share_sut" ]
            then
                cd "$workload_build_dir" && ctest_reuse_sut $filter_case $exclude_case
            else
                cd "$workload_build_dir" && TEST_CONFIG=${WORKSPACE}/test_config.yaml ctest -E "_gated$|$exclude_case" -R $filter_case -j$test_number -VV
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
            #Remove the file *.tar, if has. Issue:4976
            rm -rf $build_folder/${log}/*.tar
	    rm -rf $build_folder/${log}/.terraform
            rm -rf $build_folder/${log}/template
            #Exclude emon/collectd/svrinfo data if no performance run and user not specified to keep it.
            if [ "$performance" == "false" ] && [ "$keep_emon_collectd_data" == "false" ]
            then
                echo "Exclude emon/collectd/svr_info data"
		
                rm -rf $build_folder/${log}/*-emon
                rm -rf $build_folder/${log}/*-collectd
                rm -rf $build_folder/${log}/*-svrinfo
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
    log_folder=`ls|grep logs|grep $test_name\$`
    if [ "false" == "$performance" ]
    then 
        ./list-kpi.sh --primary $log_folder |grep ^*| while read i
        do
            echo "$i" >> "$workload_dir/kpi/$kpi.log"
        done
    else
        itr=1
        ./list-kpi.sh --primary $log_folder |grep ^* | while read i
        do
            echo itr"$itr" "$i" >> "$workload_dir/kpi/$kpi.log"
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
      prepare_build_terraform $timeout $commit
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

