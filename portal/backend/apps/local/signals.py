#
# Apache v2 license
# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#
import re

from django.db.models.signals import post_save
from django.dispatch import receiver
from local.models import LocalInstance, LocalJob
from django.utils import timezone

import os
import paramiko
import re


# @receiver(post_save, sender=CloudInstance)
# def parse_jenkins_log_when_create_instance(sender, instance, created, **kwargs):
#     #todo trigger jenkins console output parse to change password
    
#     return True


@receiver(post_save, sender=LocalJob)
def trigger_machine_status_change(sender, instance, **kwargs):

    if instance.status == "IN_QUEUE":
        print(f'task for instance: [{instance.id}] under finished')
        # machine = LocalInstance.objects.filter(ip=instance.machines[0])
        if instance.start_time > timezone.now():
            instance.status="TIME_PENDING"
            instance.save()
        # else:
        #     machine.status="FREE"
        #     machine.user = ""
        #     machine.save()
    # elif instance.status == "CREATING":
    #     log_path = f'workspace/cloud/logs/{instance.id}_change.log'
    #     if os.path.exists(log_path):
    #         os.remove(log_path)
    #     fd = open(log_path, 'w')
    #     ssh = paramiko.SSHClient()
    #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     ssh.connect(hostname='172.17.120.42', port=22, username='root', password='Password123!')
    #     cmd = f'python3 /root/monitor_jenkins.py {instance.jenkins_id} {instance.id} > /tmp/{instance.id}.log'
    #     stdin, stdout, stderr = ssh.exec_command(cmd)
    #     result = stdout.read()
    #     if not result:
    #         result = stderr.read()
    #     ssh.close()
    #     fd.write(result.decode())
    #     fd.close()
    #     print(result.decode())




