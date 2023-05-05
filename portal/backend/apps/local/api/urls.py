from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()

router.register(r'instance', LocalInstanceViewSet)
router.register(r'job', JobViewSet)
router.register(r'test_result', LocalJobTestResultViewSet)
router.register(r'workload', WorkloadViewSet)
router.register(r'component_param', ComponentParamViewSet)
router.register(r'workload_system_config', WorkloadSystemConfigViewSet)
router.register(r'instance_job_queue',LocalInstanceJobQueueViewSet)
router.register(r'local_setting', LocalSettingViewSet)
router.register(r'provison_parameter', ProvisonParameterValueSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        "parameters/",
        WorkloadSystemConfigWithParamsViewSet.as_view()),
    path(
        "provision/",
        ProvisionAPIView.as_view()),
    path(
        "upload_video_check/",
        UploadVideoCheck.as_view()),
    path(
        "schedule_check/",
        ScheduleCheck.as_view()),
    path(
        "provision_log/",
        ProvisionLogAPIView.as_view()),
    path(
        "queue/",
        ProvisionInQueueAPIView.as_view()),
    path(
        "get_config_json/",
        GetConfigJsonAPIView.as_view())
        
        
]

