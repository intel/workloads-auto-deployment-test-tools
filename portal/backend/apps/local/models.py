from django.db import models
from django.db.models.fields.related import ForeignKey
from django.contrib.postgres.fields import ArrayField


class LocalInstance(models.Model):
    STATUS_CHOICES = [
        ('FREE', 'FREE'),
        ('IN_USE','IN_USE'),
    ]
    hostname = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=30, null=True, blank=True)
    password = models.CharField(max_length=30, null=True, blank=True)
    ip = models.CharField(max_length=30, null=True, blank=True)
    ssh_port = models.PositiveIntegerField(null=True, blank=True, default=22)
    internal_ip = models.CharField(max_length=30, null=True, blank=True)
    region = models.CharField(max_length=30, null=True, blank=True)
    instance_type = models.CharField(max_length=30, null=True, blank=True)
    cpu_arch = models.CharField(max_length=30, null=True, blank=True)
    cpu_core = models.CharField(max_length=30, null=True, blank=True)
    cpu_model = models.CharField(max_length=255, null=True, blank=True)
    memory_num = models.CharField(max_length=30, null=True, blank=True)
    memory_size = models.CharField(max_length=30, null=True, blank=True)
    disk = ArrayField(models.CharField(max_length=30), default=list, blank=True, null=True)
    os = models.CharField(max_length=50, null=True, blank=True)
    k8s_role = models.CharField(max_length=50, null=True, blank=True)
    k8s_controller = models.CharField(max_length=50, null=True, blank=True)
    platform = models.CharField(max_length=30, null=True, blank=True)
    user = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES,default='FREE', null=True, blank=True)
    labels = ArrayField(models.CharField(max_length=128),
                        default=list, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        ordering = ['-id']


class LocalInstanceJobQueue(models.Model):
    STATUS_CHOICES = [
        ('IN_QUEUE', 'IN_QUEUE'),
        ('RUNNING','RUNNING'),
        ('FINISHED','FINISHED'),
    ]
    instance_id = models.PositiveIntegerField()
    job_id = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES,default='IN_QUEUE', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        ordering = ['-id']

class LocalJob(models.Model):
    # STATUS_CHOICES = [
    #     ('NOT_START', 'NOT_START'),
    #     ('IN_QUEUE', 'IN_QUEUE'),
    #     ('RUNNING', 'RUNNING'),
    #     ('PROVISIONING', 'PROVISIONING'),
    #     ('PROVISION_FAILED', 'PROVISION_FAILED'),
    #     ('BENCHMARKING', 'BENCHMARKING'),
    #     ('BENCHMARK_FAILED', 'BENCHMARK_FAILED'),
    #     ('FAILED', 'FAILED'),
    #     ('FINISHED', 'FINISHED'),
    #     ('CANCELED', 'CANCELED')
    # ]
    workload = models.CharField(max_length=128, null=True, blank=True)
    config = models.CharField(max_length=128, null=True, blank=True)
    machines = ArrayField(models.CharField(max_length=30), default=list, blank=True, null=True)
    log_url = models.CharField(max_length=128, null=True, blank=True)
    progress = models.PositiveIntegerField(null=True, blank=True, default=0, verbose_name='job progress')
    config_url = models.CharField(max_length=128, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    fail_reason = models.CharField(max_length=512, null=True, blank=True)
    provision_id = models.CharField(max_length=10, null=True, blank=True)
    user = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=30, default='IN_QUEUE', null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    filter_case = models.CharField(max_length=128, null=True, blank=True)
    result_link = models.CharField(max_length=512, null=True, blank=True)
    def __str__(self):
        return f'{self.id}'

    class Meta:
        ordering = ['-id','status']

class LocalJobTestResult(models.Model):
    TEST_RESULT_CHOICES = [
        ('PASS', 'PASS'),
        ('FAILED', 'FAILED'),
        ('NORUN', 'NORUN')
    ]
    TAG_CHOICES = [
        ('PERFORMANCE', 'PERFORMANCE'),
        ('VALIDATION', 'VALIDATION'),
        ('FUNCTION', 'FUNCTION')
    ]
    workload = models.CharField(max_length=128, null=True, blank=True)
    test_cycle = models.CharField(max_length=30, null=True, blank=True)
    commit = models.CharField(max_length=30, null=True, blank=True)
    infra_type = models.CharField(max_length=30, null=True, blank=True)
    platform = models.CharField(max_length=30, null=True, blank=True)
    test_case = models.CharField(max_length=128, null=True, blank=True)
    kpi_key = models.CharField(max_length=256, null=True, blank=True)
    kpi_value = models.CharField(max_length=50, null=True, blank=True)
    test_time = models.CharField(max_length=50, null=True, blank=True)
    instance_type = models.CharField(max_length=30, null=True, blank=True)
    test_result = models.CharField(max_length=30, choices=TEST_RESULT_CHOICES, null=True, blank=True)
    failed_reason = models.CharField(max_length=128, null=True, blank=True)
    test_date = models.CharField(max_length=50, null=True, blank=True)
    log_url = models.CharField(max_length=512, null=True, blank=True)
    cumulus_uri = models.CharField(max_length=512, null=True, blank=True)
    tag = models.CharField(max_length=512, choices=TAG_CHOICES, null=True, blank=True)
    jenkins_job_id = models.CharField(max_length=30, null=True, blank=True)
    job_id = models.CharField(max_length=30, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    itr = models.CharField(max_length=30, null=True, blank=True)
    test_from = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        ordering = ['id']

class Workload(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    owner = models.CharField(max_length=128, null=True, blank=True)
    repo_url = models.CharField(max_length=128, null=True, blank=True)
    repo_type = models.CharField(max_length=128, null=True, blank=True)
    description = models.CharField(max_length=128, null=True, blank=True)
    mail_recevier = models.CharField(max_length=128, null=True, blank=True)
    main_sender = models.CharField(max_length=128, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)



class Component(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    component_type = models.CharField(max_length=128, null=True, blank=True)
    default_version = models.CharField(max_length=128, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ComponentVersion(models.Model):
    component_id = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='component id')
    version = models.CharField(max_length=128, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ComponentParam(models.Model):
    component_id = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='component id')
    param = models.CharField(max_length=128, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class WorkloadSystemConfig(models.Model):
    workload_id = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='workload id')
    component_param_id = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='component parameter id')
    version = models.CharField(max_length=20, null=True, blank=True)
    value = models.CharField(max_length=512, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class WorkloadComponentVersion(models.Model):
    workload_id = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='component id')
    component_version_id = models.PositiveIntegerField(null=True, blank=True, default=1, verbose_name='version id')
    version = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

class ProvisonParameterValue(models.Model):
    category = models.CharField(max_length=20, null=True, blank=True)
    parameter = models.CharField(max_length=50, null=True, blank=True)
    values = ArrayField(models.CharField(max_length=256), default=list, blank=True, null=True)
    realValues = ArrayField(models.CharField(max_length=256), default=list, blank=True, null=True)

class LocalSetting(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    value = models.CharField(max_length=512, null=True, blank=True)
    def __str__(self):
        return f'{self.name}'
