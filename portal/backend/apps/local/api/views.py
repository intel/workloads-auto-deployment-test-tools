#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
import time
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from local.models import *
from local.loghandler import LogHandler
from .serializers import *

import shutil
import logging
import os
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError
import json
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from local.models import LocalSetting
import subprocess
import jenkins



LOGGER = logging.getLogger(__name__)
QUEUE_REQUEST_COUNT = 0

def escapeSingleQuotes(intstr):
    return intstr.replace("'", "\\'")

  
class LocalInstanceViewSet(viewsets.ModelViewSet):
    queryset = LocalInstance.objects.all()
    serializer_class = LocalInstanceSerializer

    def get_queryset(self):
        if self.request.query_params.get("controller"):
            return LocalInstance.objects.filter(k8s_controller=self.request.query_params.get("controller"))
        else:
            return LocalInstance.objects.all()


class LocalInstanceJobQueueViewSet(viewsets.ModelViewSet):
    queryset = LocalInstanceJobQueue.objects.all()
    serializer_class = LocalInstanceJobQueueSerializer

    def get_queryset(self):
        if self.request.query_params.get("instance_id"):
            return LocalInstanceJobQueue.objects.filter(instance_id=self.request.query_params.get("instance_id"))
        else:
            return LocalInstanceJobQueue.objects.all()


class JobViewSet(viewsets.ModelViewSet):
    queryset = LocalJob.objects.all()
    serializer_class = LocalJobSerializer

    def get_queryset(self):
        print(self.request.query_params)
        if self.request.query_params.get("user"):
            # return LocalJob.objects.filter(user=self.request.user.username)
            return LocalJob.objects.all()
        elif self.request.query_params.get("ip"):
            a = self.request.query_params.get("ip")
            return LocalJob.objects.filter(machines__overlap=a.split(","), status__in=["RUNNING","NOT_START","IN_QUEUE"])
        else:
            return LocalJob.objects.all()


class LocalJobTestResultViewSet(viewsets.ModelViewSet):
    queryset = LocalJobTestResult.objects.all()
    serializer_class = LocalJobTestResultSerializer

    def get_queryset(self):
        if self.request.query_params.get("job_id"):
            return LocalJobTestResult.objects.filter(job_id=self.request.query_params.get("job_id"))
        else:
            return LocalJobTestResult.objects.all()

    # def post(self, request, *args, **kwargs):
    #    self.request.headers = vault.setHeaders()

class ComponentParamViewSet(viewsets.ModelViewSet):
    queryset = ComponentParam.objects.all()
    serializer_class = ComponentParamSerializer

class WorkloadViewSet(viewsets.ModelViewSet):
    queryset = Workload.objects.all()
    serializer_class = WorkloadSerializer

class WorkloadSystemConfigViewSet(viewsets.ModelViewSet):
    queryset = WorkloadSystemConfig.objects.all()
    serializer_class = WorkloadSystemConfigSerializer

    def get_queryset(self):
        print(self.request.query_params)
        if self.request.query_params.get("version") and self.request.query_params.get("workload_id"):
            return WorkloadSystemConfig.objects.filter(workload_id=self.request.query_params.get("workload_id"), version=self.request.query_params.get("version"))
        if self.request.query_params.get("version_info") and self.request.query_params.get("workload_id"):
            return WorkloadSystemConfig.objects.filter(workload_id=self.request.query_params.get("workload_id")).order_by('version').values('version').distinct('version')
        else:
            return WorkloadSystemConfig.objects.all()

class WorkloadSystemConfigWithParamsViewSet(generics.ListAPIView):
    serializer_class = WorkloadSystemConfigWithParamsSerializer

    def get_queryset(self):
        default_registries = LocalSetting.objects.filter(name="default_registry")[0].value
        component_params = ComponentParam.objects.all()
        data = []
        print(self.request.query_params)
        if self.request.query_params.get("version") and self.request.query_params.get("workload_id"):
            configs = WorkloadSystemConfig.objects.filter(workload_id=self.request.query_params.get("workload_id"), version=self.request.query_params.get("version"))
            for config in configs:
                if config.component_param_id == 36:
                    data.append({"parameter": "registry", "value": default_registries})
                else:
                    data.append({"parameter":component_params.get(id=config.component_param_id).param, "value": config.value})
        return data

class ProvisionAPIView(generics.CreateAPIView):
    # queryset = LocalJob.objects.all()
    serializer_class = ProvisionSerializer 
    def post(self, request, *args, **kwargs):
        print('enter ProvisionAPIView.post() ------------------>')
        try:
            print(json.dumps(self.request.data))
            config_schema = {}
            with open("apps/local/api/config_schema.json", "r") as f:
                config_schema = json.load(f)
            if not config_schema:
                return Response("provision config config_schema.json not found.",
                    status=status.HTTP_404_NOT_FOUND)
            try:
                validate(instance=json.loads(self.request.data["config_json"]), schema=config_schema, format_checker=draft7_format_checker)
            except SchemaError as e:
                print(e.message)
                raise Exception("Check all fields")
            except ValidationError as e:
                print(e.message)
                raise Exception("Check all fields")
            val_test = ProvisionFormSerializer(data = json.loads(self.request.data["config_json"]))
            if val_test.is_valid():
                print(val_test.validated_data)
            else:
                print(val_test.errors)
                raise Exception("Check all fields")
            workload = self.request.data.get('workload')
            config_version = self.request.data.get('config_version') 
            config_json = self.request.data.get('config_json')
            machines = self.request.data.get('machines')
            schedule_time = self.request.data.get('schedule_time')
            start_time = parse_datetime(schedule_time[0])
            end_time = parse_datetime(schedule_time[1])
            print(start_time, end_time)
            queue_jobs = LocalJob.objects.filter(machines__overlap=machines, status__in=["RUNNING","TIME_PENDING","IN_QUEUE"])
            for queue_job in queue_jobs:
                print(queue_job.start_time,queue_job.end_time)
                if (start_time > queue_job.start_time and start_time < queue_job.end_time) or (end_time > queue_job.start_time and end_time < queue_job.end_time):
                    return Response(f"job {queue_job.id} already booked machine {queue_job.machines}",
                            status=status.HTTP_409_CONFLICT)
            config = json.loads(config_json)
            if config.get("smtp","") == "default":
                config["smtp"] = ""
            if config.get("sender","") == "default@default.com":
                config["sender"] = ""
            if config.get("receivers","") == "default@default.com":
                config["receivers"] = ""
            if config.get("exclude_case","") == "default":
                config["exclude_case"] = ""
            if config.get("ctest_option","") == "default":
                config["ctest_option"] = ""
            filter_case = config.get('filter_case')
            job = LocalJob.objects.create(workload=workload,machines=machines,config=config_version,filter_case=filter_case, start_time=start_time, end_time=end_time, user=self.request.user.username)
            config["jobId"] = str(job.id)
            config_output = json.dumps(config)
            config_file_path = f'workspace/local/logs/{job.id}_config.json'
            log_file_path = f'workspace/local/logs/{job.id}_provision.log'
            if not os.path.exists(os.path.dirname(config_file_path)):
                os.makedirs(os.path.dirname(config_file_path))
            if os.path.isfile(config_file_path):
                os.remove(config_file_path)
            if not os.path.isfile(log_file_path):
                with open(log_file_path, 'w') as f:
                    f.write(" ")
            fd = open(config_file_path, 'w')
            fd.write(config_output)
            fd.close()
            return Response("trigger provision successfully",
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            print(ex)
            return Response(f"Failed to trigger provision: {ex}",
                            status=status.HTTP_400_BAD_REQUEST)

class ScheduleCheck(generics.CreateAPIView):
    # queryset = LocalJob.objects.all()

    serializer_class = SchedulerSerializer 
    tzname = timezone.get_current_timezone()
    def intel_host_check(self, all_machines):
        check_result = []
        hosts_info = LocalInstance.objects.filter(ip__in=all_machines).values()
        for host in hosts_info:
            result = os.popen(f'ssh -o StrictHostKeyChecking=no {host["username"]}@{host["ip"]} -p {host["ssh_port"]} \
                    lscpu |grep "Model name:"|grep -o "Intel(R)"').read().strip()
            if result != "Intel(R)":
                check_result.append(f"Please check {host['hostname']} {host['ip']} available for backend docker container and CPU type is Intel.")
        return check_result

    def post(self, request, *args, **kwargs):
        try:
            machines = [host["ip"] for host in self.request.data.get('machines', [])]
            start_time = self.request.data.get('start_time')
            end_time = self.request.data.get('end_time')
            start_time = parse_datetime(start_time)
            end_time = parse_datetime(end_time)
            job_occupant = LocalInstance.objects.filter(ip=machines[0])[0].occupant_job
            # queue_jobs = LocalJob.objects.filter(machines__overlap=machines, status__in=["RUNNING","TIME_PENDING" ,"IN_QUEUE"]).values()
            queue_jobs = LocalJob.objects.filter(id=int(job_occupant)).values()
            conflicted_jobs = []
            for queue_job in queue_jobs:
                # print(queue_job.get("start_time"),queue_job.get("end_time"))
                # print(queue_job.get("start_time").astimezone(tz=tzname))
                # print(start_time,end_time)
                if (start_time > queue_job.get("start_time") and start_time < queue_job.get("end_time")) or (end_time > queue_job.get("start_time") and end_time < queue_job.get("end_time")):
                    queue_job["start_time"] = queue_job.get("start_time").astimezone(tz=self.tzname)
                    queue_job["end_time"] = queue_job.get("end_time").astimezone(tz=self.tzname)
                    conflicted_jobs.append(queue_job)
            if conflicted_jobs:
                return Response(conflicted_jobs, status.HTTP_200_OK)

            check_result = self.intel_host_check(machines)
            if check_result:
               return Response({check_result},
                      status=status.HTTP_400_BAD_REQUEST)
            return Response({"trigger schedule checking successfully"},
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({f"Failed to trigger provision: {ex}"},
                            status=status.HTTP_400_BAD_REQUEST)

class ProvisionLogAPIView(generics.ListAPIView):
    # queryset = LocalJob.objects.all()
    serializer_class = ProvisionLogSerializer 

    def get_queryset(self):
        try:
            print(self.request.query_params)
            job_id = self.request.query_params.get('job_id')
            log_file = f"workspace/local/logs/{job_id}_provision.log"
            content = "No log yet"
            with open(log_file) as f:
                content = f.read()
            return [{"data": content}]
        except Exception as ex:
            return [{"data": f"fail to get log: {ex}"}]

    def post(self, *args, **kwargs):
        job_id = self.request.query_params.get('job_id')
        LogHandler(job_id).sendlog(self.request.data["data"])
        return Response("Write log to job log", status.HTTP_200_OK)


class ProvisionInQueueAPIView(generics.CreateAPIView):
    queryset = LocalJob.objects.all()
    serializer_class = LocalJobSerializer
    cmd_url = f'curl -H "X-Vault-Token: {os.environ["VAULT_TOKEN"]}" -H "X-Vault-Namespace: kv" -X GET {os.environ["VAULT_ADDR"]}/v1/kv/wsf-secret-password'
    cmd_result_url = subprocess.Popen(cmd_url, shell=True, stdout=subprocess.PIPE).communicate()[0]
    cmd_token = f'curl -H "X-Vault-Token: {os.environ["VAULT_TOKEN"]}" -H "X-Vault-Namespace: kv" -X GET {os.environ["VAULT_ADDR"]}/v1/kv/wsf-secret-password2'
    cmd_result_token = subprocess.Popen(cmd_token, shell=True, stdout=subprocess.PIPE).communicate()[0]

    # jenkins_token = subprocess.check_output(['vault', 'kv', 'get', '-mount=kv', '-field=TWDTJenkinsToken', 'wsf-secret-password2']).decode('utf-8')
    # jenkins_url = subprocess.check_output(['vault', 'kv', 'get', '-mount=kv', '-field=JenkinsUrl', 'wsf-secret-password']).decode('utf-8')
    jenkins_token = json.loads(cmd_result_token.decode('utf8'))["data"]["TWDTJenkinsToken"]
    jenkins_url = json.loads(cmd_result_url.decode('utf8'))["data"]["JenkinsUrl"]
    jenkinsClient = jenkins.Jenkins(jenkins_url, "admin", jenkins_token)

    def get(self, request, *args, **kwargs):
        # todo: check if job already exist and not finished(canceled or pass or fail)
        global QUEUE_REQUEST_COUNT 
        QUEUE_REQUEST_COUNT += 1

        start_one_job_id = self.request.query_params.get('start_job_id')
        stop_job_id = self.request.query_params.get('stop_job_id')
        user = request.user.username
        try:
            jobs = LocalJob.objects.filter(status__in=["RUNNING","STARTING"])
            if start_one_job_id and int(start_one_job_id) not in [job.id for job in jobs]:
                return self.start_one_job(start_one_job_id, user)
                   
            if stop_job_id:
                job_stop = LocalJob.objects.filter(id=int(stop_job_id))[0]
                LogHandler(stop_job_id).sendlog("Trying to stop job")
                if job_stop.status != "RUNNING":
                    return Response(f"Job {job_stop.id} no need to stop",
                        status=status.HTTP_200_OK)
                else:
                    self.jenkinsClient.stop_build("full_benchmark", int(job_stop.provision_id.split("//")[1].split("/")[-1])) 
                    return Response(f"Stop Job {job_stop.id} , Jenkins job id: {job_stop.provision_id}.",
                        status=status.HTTP_201_CREATED)

            job_status_flag = False
            for job in jobs:
                job_status_flag_tmp = self.update_job(job)
                if job_status_flag_tmp:
                    if not job_status_flag:
                        job_status_flag = True
                    
            jobs = LocalJob.objects.filter(status__in=["IN_QUEUE"])
            for job in jobs:
                machine_queryset = LocalInstance.objects.filter(ip__in=job.machines)
                print(job.machines)
                machine = machine_queryset[0]
                if machine.occupant_job:
                    job_occupant_queryset = LocalJob.objects.filter(id=int(machine.occupant_job))
                    if job_occupant_queryset.count() == 0:
                        machine_queryset.update(status="FREE", occupant_job="")
                        LogHandler(job_occupant).sendlog(f"Release machine {machine.hostname} {machine.ip}")
                    else:
                        job_occupant = job_occupant_queryset[0]
                        if job_occupant.end_time < timezone.now():
                            machine_queryset.update(status="FREE", occupant_job="")
                            LogHandler(job_occupant).sendlog(f"Release machine {machine.hostname} {machine.ip}")

                if machine.status == "IN_USE" and machine.occupant_job != str(job.id):
                   print(f"abort job {job.id} to run, because cluster {machine.ip} is using.")
                else:
                    if job.start_time < timezone.now() and job.end_time > timezone.now():
                        self.start_job(job, user)
                    else:
                        job.status = "TIME_PENDING"
                        job.save()
                        LogHandler(job.id).sendlog(f"Going into TIME_PENDING status")
                    if not job_status_flag:
                        job_status_flag = True

            jobs_pending = LocalJob.objects.filter(status="TIME_PENDING")
            for job in jobs_pending:
                print(job.start_time, timezone.now())
                if job.start_time < timezone.now():
                    if not job_status_flag:
                        job_status_flag = True
                    job.status = "IN_QUEUE"
                    job.save()
                    LogHandler(job.id).sendlog(f"Going into IN_QUEUE status")
                   
            if job_status_flag:
                return Response(f"trigger queue job successfully.",
                                status=status.HTTP_201_CREATED)
            if QUEUE_REQUEST_COUNT > 10:
                QUEUE_REQUEST_COUNT = 0
                return Response(f"trigger queue job successfully.",
                                status=status.HTTP_201_CREATED)
            return Response(f"trigger queue job successfully.",
                            status=status.HTTP_200_OK)
        except Exception as ex:

            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # print(exc_type, fname, exc_tb.tb_lineno)
            return Response(f"Failed to trigger provison: {ex}",
                            status=status.HTTP_400_BAD_REQUEST)

    def start_one_job(self, start_job_id, user):
        job_start_queryset = LocalJob.objects.filter(id=int(start_job_id))
        job_start = job_start_queryset[0]
        if job_start.end_time < timezone.now():
            return Response(f"job {job_start.id} could not start, end time is {job_start.end_time}, out of date.", status=status.HTTP_200_OK)
        machines = LocalInstance.objects.filter(ip__in=job_start.machines)
        can_start_job = True
        for machine in machines:
            if machine.status == "IN_USE" or machine.occupant_job and machine.occupant_job != start_job_id:
                can_start_job = False
                break
        if job_start.status in ["RUNNING", "TIME_PENDING", "IN_QUEUE", "STARTING"]:
            return Response(f"Job {job_start.id} in {job_start.status} status.",
                        status=status.HTTP_200_OK)
        elif can_start_job:
            return self.start_job(job_start, user)      

        else:
            job_start_queryset.update(status="IN_QUEUE")
            return Response(f"job {job_start.id} could not start, wait {machines[0].occupant_job} to release {job_start.machines}.",
                        status=status.HTTP_201_CREATED)
        
    def update_jenkins_params(self, config_json):
        hostip = self.jenkins_url.split("//")[1].split(":")[0]
        jenkins_params = {}       
        jenkins_params.update({
            "front_job_id": config_json["jobId"],  
            "platforms": config_json["platforms"],   
            "sf_commit": config_json["commit"],  
            "repo": config_json["jsf_repo"],     
            "registry": config_json["registry"],  
            "instance_api": f"https://{hostip}:8899/local/api/instance/", 
            "artifactory_url": f"http://{hostip}:8082/artifactory", 
            "django_execution_result_url": f"https://{hostip}:8899/local/api/test_result/",
            "session": "",
            "workload_list": config_json["workloadName"],
            "customer": "main",
            "emon": False,
            "baremetal": True,
            "vm": False,
            "tdx": False,
            "snc4": False,
            "filter_case": config_json["filter_case"],
            "exclude_case": config_json["exclude_case"],
            "cumulus_tags": "",
            "run_on_previous_hw": True,
            "cluster_file": "cluster.yaml",
            "limited_node_number": 4,
            "workload_params": config_json["workload_parameter"].strip(),
            "workload_test_config_yaml": "",
            "controller_ip": config_json["deployHost"][0]["ip"],
            "worker_ip_list": ",".join([ host["ip"] for host in config_json["deployHost"][1:]]),
            "k8s_reset": False if config_json["kubernetes_deploy"] !="true" else True,
            "ctest_option": config_json["ctest_option"],
            })
        return jenkins_params
    
    def start_job(self, job, user):
        print(f"Trigger job: {job.id}")
        job_choice = LocalJob.objects.filter(id=job.id)
        job_choice.update(status="STARTING", provision_id="")
        machine = LocalInstance.objects.filter(ip__in=job.machines)
        machine.update(status="IN_USE", user=user, occupant_job=job.id)
        try:
            config_json = {}
            with open(f'workspace/local/logs/{job.id}_config.json') as fd:
                config_json = json.load(fd)
            if not config_json:
                return Response("could not find {job.id}_config.json",
                                    status=status.HTTP_404_NOT_FOUND)
            jenkins_params = self.update_jenkins_params(config_json=config_json)
            print(jenkins_params)
            new_job = self.jenkinsClient.build_job("full_benchmark", jenkins_params)
            build_new = self.jenkinsClient.get_queue_item(new_job)
            tries = 0
            while 'executable' not in build_new:
                build_new = self.jenkinsClient.get_queue_item(new_job)
                time.sleep(3)
                tries += 1
                if tries > 20:
                    return Response("trigger provision timeout",
                                        status=status.HTTP_404_NOT_FOUND)
            build_id = build_new['executable']['number']
            # build_id=29
        except Exception as e:
            job_choice.update(status="FAILURE")
            machine.update(status="FREE",user="",occupant_job="")
            LogHandler(job.id).sendlog(f"Starting failed, {str(e)}")
        print("full_benchmark job id: ", build_id)
        job_choice.update(provision_id=f"{self.jenkins_url}/full_benchmark/job/{str(build_id)}")
        job_choice.update(status="RUNNING")
        LogHandler(job.id).sendlog(f"Jenkins task triggered successfully, please visit {self.jenkins_url}/job/full_benchmark/{str(build_id)} for more information.")
        # print(jenkins_params)
        return Response(f"Start job {job_choice[0].id} successfully.",
            status=status.HTTP_201_CREATED)

    def update_job(self, job):
        job_id = job.provision_id
        job_changed = False
        if not job_id:
            print(f"No jenkins job id yet for {job.id}")
        if job_id:
            job_info = self.jenkinsClient.get_build_info("full_benchmark", int(job_id.split("/")[-1]))
            if 'result' in job_info.keys() and  job_info.get('result') is not None:
                job_status = job_info['result']
                print(f"Job {job_id} status:", job_status)
                LogHandler(job.id).sendlog(f"Job in {job_status} status")
                job.status=job_status
                job.save()
                job_changed = True
                if job_status not in ["RUNNING","STARTING"]:
                    LocalInstance.objects.filter(ip__in=job.machines).update(status="FREE")
                    
        return job_changed
    
class ProvisonParameterValueSet(viewsets.ModelViewSet):
    queryset = ProvisonParameterValue.objects.all()
    serializer_class = ProvisionParameterSerializer
    def list(self, request, *args, **kwargs):
        data = {}
        for category in ProvisonParameterValue.objects.distinct('category'):
            current_category = escapeSingleQuotes(category.category)
            data[current_category] = {}
            for parameter in ProvisonParameterValue.objects.filter(category=current_category).distinct("parameter"):
                current_parameter = escapeSingleQuotes(parameter.parameter)
                data[current_category][current_parameter] = []
                if category.category == "system" and parameter.parameter == "biosArgs":
                    valueMapping = {}
                    for val in ProvisonParameterValue.objects.filter(category=current_category, parameter=current_parameter):
                        data[category.category][parameter.parameter].append({"value": val.values[0]})
                        valueMapping[val.values[0]] = val.realValues
                    data[category.category]["valueMapping"] = valueMapping
                else:
                    for v in parameter.values:
                        data[category.category][parameter.parameter].append({"value":v})
        return Response(data = data, status=200)
    
class GetConfigJsonAPIView(generics.CreateAPIView):

    def get(self, request, *args, **kwargs):
        try:
            json_file = request.query_params.get("json_file", None)
            json_file = json_file.replace("../", "").replace("/", "")
            res = os.popen("stat workspace/local/logs/"+json_file).read()
            if "symbolic link" in res:
                raise Exception
            elif "regular file" in res:
                if not "Links: 1" in res:
                    raise Exception
            with open("workspace/local/logs/"+json_file, "r") as fp:
                res = json.load(fp)
            return Response(data = res,
                            status=200)
        except Exception as ex:
            return Response(f"Failed to get json: {ex}",
                            status=404)

class LocalSettingViewSet(viewsets.ModelViewSet):
    queryset = LocalSetting.objects.all()
    serializer_class = LocalSettingSerializer

    def get_queryset(self):
        if self.request.query_params.get("name"):
            return LocalSetting.objects.filter(name=self.request.query_params.get("name"))
        else:
            return LocalSetting.objects.all()

class UploadVideoCheck(generics.CreateAPIView):
    serializer_class = SchedulerSerializer 
    def post(self, request, *args, **kwargs):
        try:
            print(self.request.data)
            video_files = self.request.FILES.getlist('files')
            upload_video_path = f'workspace/local/media/'

            if not os.path.exists(upload_video_path):
                os.mkdir(upload_video_path)
            else:
                shutil.rmtree(upload_video_path)
                os.mkdir(upload_video_path) 


            for video_item in video_files:
                with open(upload_video_path+video_item.name, 'wb+') as f:
                    for chunk in video_item.chunks():
                        f.write(chunk)
                    f.close()
            return Response(f"Received successful", status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(f"Failed to upload video file: {ex}",
                            status=status.HTTP_400_BAD_REQUEST)
