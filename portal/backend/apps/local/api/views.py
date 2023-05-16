from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from local.models import *
from .serializers import *
from taas.utils import vault

import shutil
import logging
import os
import paramiko
import requests
from jsonschema import validate, draft7_format_checker
from jsonschema.exceptions import SchemaError, ValidationError
import json
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from local.models import LocalSetting
from pathlib import Path

LOGGER = logging.getLogger(__name__)

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
        component_params = ComponentParam.objects.all()
        data = []
        print(self.request.query_params)
        if self.request.query_params.get("version") and self.request.query_params.get("workload_id"):
            configs = WorkloadSystemConfig.objects.filter(workload_id=self.request.query_params.get("workload_id"), version=self.request.query_params.get("version"))
            for config in configs:
                data.append({"parameter":component_params.get(id=config.component_param_id).param, "value": config.value})
        return data


class ProvisionAPIView(generics.CreateAPIView):
    # queryset = LocalJob.objects.all()
    serializer_class = ProvisionSerializer 
    def post(self, request, *args, **kwargs):
        print('enter ProvisionAPIView.post() ------------------>')
        self.request.headers = vault.setHeaders()
        try:
            provision_server_url = LocalSetting.objects.get(name='provision_server_url').value
            provision_server_url = f"{provision_server_url}/conf/createconf"
            print(self.request.data)
            if Path("apps/local/api/config_schema.json").is_symlink():
                raise Exception("This application refuse to proceed file that is symlink")
            with open("apps/local/api/config_schema.json", "r") as f:
                config_schema = json.load(f)
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
            start_time = self.request.data.get('start_time')
            end_time = self.request.data.get('end_time')
            start_time = parse_datetime(start_time)
            end_time = parse_datetime(end_time)
            print(start_time)
            queue_jobs = LocalJob.objects.filter(machines__overlap=machines, status__in=["RUNNING","NOT_START","IN_QUEUE"])
            for queue_job in queue_jobs:
                print(queue_job.start_time,queue_job.end_time)
                if (start_time > queue_job.start_time and start_time < queue_job.end_time) or (end_time > queue_job.start_time and end_time < queue_job.end_time):
                    return Response(f"job {queue_job.id} already booked machine {queue_job.machines}",
                            status=status.HTTP_409_CONFLICT)
            config = json.loads(config_json)
            filter_case = config.get('filter_case')
            job = LocalJob.objects.create(workload=workload,machines=machines,config=config_version,filter_case=filter_case, start_time=start_time, end_time=end_time, user=self.request.user.username)
            config["jobId"] = str(job.id)
            video_download_link = "https://" + config["registry"].split(':')[0] + ':8899/local/media/'
            videos = os.listdir(f'workspace/local/media')
            if len(videos) != 0:
                if len(config["workload_parameter"]) != 0:
                    config["workload_parameter"] += " "
                config["workload_parameter"] += "VIDEO_URL_PREFIX=" + video_download_link
                config["workload_parameter"] += " " + "VIDEO_FILENAMES=" + ','.join(videos)
                config["workload_parameter"] += " " + "INFERENCE_STREAMS=1"
            config_output = json.dumps(config)
            config_file_path = f'workspace/local/logs/{job.id}_config.json'
            if os.path.exists(config_file_path):
                os.remove(config_file_path)
            fd = open(config_file_path, 'w')
            fd.write(config_output)
            fd.close()
            machines = LocalInstance.objects.filter(ip__in=machines)
            # for machine in machines:
            #     LocalInstanceJobQueue.objects.create(job_id=job.id,instance_id=machine.id)
            # for machine in machines:
            #     if machine.status == "IN_USE":
            #         job.status="IN_QUEUE"
            #         job.user=self.request.user.username
            #         job.save()
            #         break
            # else:
            #     job.status="RUNNING"
            #     job.user=self.request.user.username
            #     job.save()
            #     for machine in machines:
            #         machine.status = "IN_USE"
            #         machine.user = self.request.user.username
            #         machine.save()
            #     print(requests.post(provision_server_url,data=config_output))
            return Response("trigger provision successfully",
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response(f"Failed to trigger provision: {ex}",
                            status=status.HTTP_400_BAD_REQUEST)

class ScheduleCheck(generics.CreateAPIView):
    # queryset = LocalJob.objects.all()
    serializer_class = SchedulerSerializer 
    def intel_host_check(self, all_machines):
        check_result = []
        hosts_info = LocalInstance.objects.filter(ip__in=all_machines).values()
        for host in hosts_info:
            result = os.popen(f'sshpass -p {host["password"]} ssh -o StrictHostKeyChecking=no {host["username"]}@{host["ip"]} -p {host["ssh_port"]} \
                    lscpu |grep "Model name:"|grep -o "Intel(R)"').read().strip()
            if result != "Intel(R)":
                check_result.append({host["ip"]:f"Please check {host['hostname']} {host['ip']} available and CPU type is Intel."})
        return check_result

    def post(self, request, *args, **kwargs):
        try:
            print(self.request.data)
            machines = self.request.data.get('machines')
            check_result = self.intel_host_check(machines)
            if check_result:
               return Response({"result":check_result},
                      status=status.HTTP_400_BAD_REQUEST)
            start_time = self.request.data.get('start_time')
            end_time = self.request.data.get('end_time')
            start_time = parse_datetime(start_time)
            end_time = parse_datetime(end_time)
            print(start_time)
            queue_jobs = LocalJob.objects.filter(machines__overlap=machines, status__in=["RUNNING","NOT_START","IN_QUEUE"])
            for queue_job in queue_jobs:
                print(queue_job.start_time,queue_job.end_time)
                if (start_time > queue_job.start_time and start_time < queue_job.end_time) or (end_time > queue_job.start_time and end_time < queue_job.end_time):
                    return Response(f"job {queue_job.id} already booked machine {queue_job.machines}",
                            status=status.HTTP_409_CONFLICT)

            return Response({"result":"trigger provision successfully"},
                            status=status.HTTP_201_CREATED)
            # return Response(f"Failed to trigger provision: testttttttt",
            #                 status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'result':f"Failed to trigger provision: {ex}"},
                            status=status.HTTP_400_BAD_REQUEST)

class ProvisionLogAPIView(generics.ListAPIView):
    # queryset = LocalJob.objects.all()
    serializer_class = ProvisionLogSerializer 
    def get_queryset(self):
        
        try:
            print(self.request.query_params)
            job_id = self.request.query_params.get('job_id')
            provision_server_url = LocalSetting.objects.get(name='provision_server_url').value
            provision_server_url = f"{provision_server_url}/file/download/provision.log/{job_id}"
            log_file_path = f'workspace/local/logs/{job_id}_provision.log'
            headers = vault.setHeaders()
            data = ""
            data = requests.post(provision_server_url, headers=headers, verify="/backend/cert/cert.pem")
            a = json.loads(data.content)
            # print(a["logContent"])
            if os.path.exists(log_file_path):
                os.remove(log_file_path)
            fd = open(log_file_path, 'w') 
            fd.write(a["logContent"])
            fd.close()
            if Path(log_file_path).is_symlink():
                return [{"data": "This application refuse to proceed file that is symlink"}]
            fd = open(log_file_path, 'r')
            content = fd.read()
            fd.close()
            return [{"data": content}]
        except Exception as ex:
            return [{"data": f"fail to get log: {ex}"}]


class ProvisionInQueueAPIView(generics.CreateAPIView):
    queryset = LocalJob.objects.all()
    serializer_class = LocalJobSerializer

    def get(self, request, *args, **kwargs):
        # todo: check if job already exist and not finished(canceled or pass or fail)
        try:
            provision_server_url = LocalSetting.objects.get(name='provision_server_url').value
            provision_server_url = f"{provision_server_url}/conf/createconf"
            jobs = LocalJob.objects.filter(status="IN_QUEUE")
            headers = vault.setHeaders()
            for job in jobs:
                job_machines = job.machines
                escape_machines = list(map(lambda x:escapeSingleQuotes(x),job_machines))
                machines = LocalInstance.objects.filter(ip__in=escape_machines)
                in_use = 0
                for machine in machines:
                    print(f"Machine: {machine.ip}")
                    print(f"Status: {machine.status}")
                    if machine.status == "IN_USE":
                        in_use+=1
                if in_use > 0:
                    pass
                else:
                    if job.start_time < timezone.now() and job.end_time > timezone.now():
                        print(f"Trigger job: {job.id}")
                        config_file_path = f'workspace/local/logs/{job.id}_config.json'
                        if Path(config_file_path).is_symlink():
                            return Response("This application refuse to proceed file that is symlink",
                            status=status.HTTP_400_BAD_REQUEST)
                        fd = open(config_file_path, 'r')
                        config = fd.read()
                        fd.close()
                        job.status="RUNNING"
                        job.save()
                        for machine in machines:
                            machine.status = "IN_USE"
                            machine.user = job.user
                            machine.save()
                        requests.post(provision_server_url, data=config, headers=headers, verify="/backend/cert/cert.pem")
                        print(provision_server_url)
                        # print(result.decode())
            jobs_pending = LocalJob.objects.filter(status="TIME_PENDING")
            for job in jobs_pending:
                job_machines = job.machines
                escape_machines = list(map(lambda x:escapeSingleQuotes(x),job_machines))
                if job.end_time < timezone.now():
                    job.status = "FINISHED"
                    job.save()
                    machines = LocalInstance.objects.filter(ip__in=escape_machines)
                    for machine in machines:
                        if machine.status == "IN_USE":
                            machine.status="FREE"
                            machine.user = ""
                            machine.save()
            return Response("trigger provision successfully",
                            status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response(f"Failed to trigger provison: {ex}",
                            status=status.HTTP_400_BAD_REQUEST)

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


            for i, video_item in enumerate(video_files):
                with open(upload_video_path+"upload_file_"+str(i)+".mp4", 'wb+') as f:
                    for chunk in video_item.chunks():
                        f.write(chunk)
                    f.close()
            return Response(f"Received successful", status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(f"Failed to upload video file: {ex}",
                            status=status.HTTP_400_BAD_REQUEST)
