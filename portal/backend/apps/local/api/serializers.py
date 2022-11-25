from rest_framework import serializers

from local.models import *


class LocalInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalInstance
        fields = '__all__'


class LocalJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalJob
        fields = '__all__'


class WorkloadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workload
        fields = '__all__'


class WorkloadSystemConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkloadSystemConfig
        fields = '__all__'


class ComponentParamSerializer(serializers.ModelSerializer):

    class Meta:
        model = ComponentParam
        fields = '__all__'


class WorkloadSystemConfigWithParamsSerializer(serializers.Serializer):
    parameter = serializers.CharField(max_length=120)
    value = serializers.CharField(max_length=512)


class ProvisionSerializer(serializers.Serializer):
    workload = serializers.CharField(max_length=120)
    config_version = serializers.CharField(max_length=512)
    config_json = serializers.CharField(max_length=512)
    machines = serializers.ListField(max_length=50)

class SchedulerSerializer(serializers.Serializer):
    start_time = serializers.CharField(max_length=120)
    end_time = serializers.CharField(max_length=512)
    machines = serializers.ListField(max_length=50)

class ProvisionLogSerializer(serializers.Serializer):
    data = serializers.CharField(max_length=1024)

class LocalInstanceJobQueueSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LocalInstanceJobQueue
        fields = '__all__'


class ProvisionParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvisonParameterValue
        fields = '__all__'

def CheckBoolean(value):
    if value not in ["true", "false"]:
        raise serializers.ValidationError("Not in true or false")

def CheckInteger(value):
    if value != "":
        try:
            int(value)
        except:
            raise serializers.ValidationError("Should be integer")

class deployHostFormSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    ansible_host = serializers.IPAddressField(required=True)
    ip = serializers.IPAddressField(required=True)
    username = serializers.CharField(required=True)
    hostname = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class kubernetesArgsFormSerializer(serializers.Serializer):
    kube_version = serializers.CharField(allow_blank=True)
    kube_network_plugin = serializers.CharField(allow_blank=True)
    container_manager = serializers.CharField(allow_blank=True)
    dashboard_enabled = serializers.CharField(required=True, validators=[CheckBoolean])
    helm_enabled = serializers.CharField(required=True, validators=[CheckBoolean])
    registry_enabled = serializers.CharField(required=True, validators=[CheckBoolean])
    ingress_nginx_enabled = serializers.CharField(required=True, validators=[CheckBoolean])
    ingress_nginx_host_network = serializers.CharField(required=True, validators=[CheckBoolean])
    krew_enabled = serializers.CharField(required=True, validators=[CheckBoolean])

    def validate_kube_network_plugin(self, value):
        if value not in ["", "cilium", "calico", "weave", "flannel"]:
            raise serializers.ValidationError("kube network plugin Not in cilium, calico, weave or flannel")

    def validate_container_manager(self, value):
        if value not in ["", "docker", "crio", "containerd"]:
            raise serializers.ValidationError("kube network plugin Not in docker, crio or containerd")

class softwarepackageArgsFormSerializer(serializers.Serializer):
    Name = serializers.CharField(required=True)
    scriptArgs = serializers.CharField(required=True)

class vmosArgsFormSerializer(serializers.Serializer):
    osNumber = serializers.CharField(allow_blank=True, validators=[CheckInteger])
    osType = serializers.CharField(allow_blank=True)
    vmName = serializers.CharField(allow_blank=True)
    memory = serializers.CharField(allow_blank=True, validators=[CheckInteger])
    cpuNumber = serializers.CharField(allow_blank=True, validators=[CheckInteger])
    disk = serializers.CharField(allow_blank=True, validators=[CheckInteger])

class ProvisionFormSerializer(serializers.Serializer):
    deployHost = serializers.ListField(required=True, child=deployHostFormSerializer())
    platforms = serializers.CharField(required=True)
    kubernetes_deploy = serializers.CharField(required=True, validators=[CheckBoolean])
    kubernetesInstallMethod = serializers.CharField(allow_blank=True)
    kubernetesArgs = kubernetesArgsFormSerializer()
    jenkins = serializers.CharField(required=True, validators=[CheckBoolean])
    workloadName = serializers.CharField(required=True)
    jsf_repo = serializers.CharField(required=True)
    commit = serializers.CharField(required=True)
    registry = serializers.CharField(required=True)
    filter_case = serializers.CharField(allow_blank=True)
    softwarepackage = serializers.CharField(required=True, validators=[CheckBoolean])
    softwarepackageArgs = serializers.ListField(required=False, child=softwarepackageArgsFormSerializer())
    system_deploy = serializers.CharField(required=True, validators=[CheckBoolean])
    Kernel_update = serializers.CharField(required=True, validators=[CheckBoolean])
    kernelVersion = serializers.CharField(allow_blank=True)
    kernelArgs_update = serializers.CharField(required=True, validators=[CheckBoolean])
    kernelArgs = serializers.CharField(allow_blank=True)
    vm_deploy = serializers.CharField(required=True, validators=[CheckBoolean])
    vm_docker = serializers.CharField(allow_blank=True, validators=[CheckBoolean])
    vmosArgs = vmosArgsFormSerializer()
    sender = serializers.EmailField(required=True)
    receivers = serializers.EmailField(required=True)

    def validate_platforms(self, value):
        if value not in ["ICX", "SPR"]:
            raise serializers.ValidationError("Platforms Not in ICX or SPR")

    def validate_kubernetesInstallMethod(self, value):
        if value not in ["", "host", "vm", "docker"]:
            raise serializers.ValidationError("kubernetesInstallMethod Not in host, vm or docker")
