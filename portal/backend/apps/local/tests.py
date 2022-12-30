from django.test import TestCase
# from .models import Workload
from apps.local.api.views import *

# Create your tests here.
class ViewTest(TestCase):
    def setUp(self):
        pass

    def test_local_instance_view(self):
        instance_view = LocalInstanceViewSet()
        self.assertEqual(isinstance(instance_view, LocalInstanceViewSet), True)

    def test_local_instance_job_queue_view(self):
        instance_Job_queue_view = LocalInstanceJobQueueViewSet()
        self.assertEqual(isinstance(instance_Job_queue_view, LocalInstanceJobQueueViewSet), True)
    
    def test_job_view(self):
        job_view = JobViewSet()
        self.assertEqual(isinstance(job_view, JobViewSet), True)
    
    def test_component_para_view(self):
        component_para_view = ComponentParamViewSet()
        self.assertEqual(isinstance(component_para_view, ComponentParamViewSet), True)
    
    def test_workload_view(self):
        workload_view = WorkloadViewSet()
        self.assertEqual(isinstance(workload_view, WorkloadViewSet), True)
    
    def test_workload_system_config_view(self):
        workload_system_config_view = WorkloadSystemConfigViewSet()
        self.assertEqual(isinstance(workload_system_config_view, WorkloadSystemConfigViewSet), True)
    
    def test_workload_system_config_with_para_view(self):
        workload_system_config_with_para_view = WorkloadSystemConfigWithParamsViewSet()
        self.assertEqual(isinstance(workload_system_config_with_para_view, WorkloadSystemConfigWithParamsViewSet), True)

    def test_provision_api_view(self):
        provision_api_view = ProvisionAPIView()
        self.assertEqual(isinstance(provision_api_view, ProvisionAPIView), True)
    
    def test_schedule_check_view(self):
        schedule_check_view = ScheduleCheck()
        self.assertEqual(isinstance(schedule_check_view, ScheduleCheck), True)
    
    def test_provision_log_api_view(self):
        provision_log_api_view = ProvisionLogAPIView()
        self.assertEqual(isinstance(provision_log_api_view, ProvisionLogAPIView), True)
    
    def test_provision_in_queue_view(self):
        provision_in_queue_view = ProvisionInQueueAPIView()
        self.assertEqual(isinstance(provision_in_queue_view, ProvisionInQueueAPIView), True)
    
    def test_provision_para_valueset(self):
        provision_para_valueset = ProvisonParameterValueSet()
        self.assertEqual(isinstance(provision_para_valueset, ProvisonParameterValueSet), True)
    
    def test_get_config_json_view(self):
        get_config_json_view = GetConfigJsonAPIView()
        self.assertEqual(isinstance(get_config_json_view, GetConfigJsonAPIView), True)
    
    def tearDown(self):
        pass