from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import *


class LocalInstanceAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in LocalInstance._meta.fields]

class LocalInstanceJobQueueAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in LocalInstanceJobQueue._meta.fields]

class JobAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in LocalJob._meta.fields]

class WorkloadAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in Workload._meta.fields]

class ComponentAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in Component._meta.fields]

class ComponentVersionAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ComponentVersion._meta.fields]

class ComponentParamAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ComponentParam._meta.fields]

class WorkloadSystemConfigAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in WorkloadSystemConfig._meta.fields]

class WorkloadComponentVersionAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in WorkloadComponentVersion._meta.fields]

class ProvisonParameterValueAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in ProvisonParameterValue._meta.fields]

class LocalSettingAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in LocalSetting._meta.fields]

class LocalTestResultAdmin(ImportExportModelAdmin):
    list_display = [field.name for field in LocalJobTestResult._meta.fields]

admin.site.register(LocalInstance, LocalInstanceAdmin)
admin.site.register(LocalInstanceJobQueue, LocalInstanceJobQueueAdmin)
admin.site.register(LocalJob, JobAdmin)
admin.site.register(LocalSetting, LocalSettingAdmin)
admin.site.register(WorkloadComponentVersion, WorkloadComponentVersionAdmin)
admin.site.register(WorkloadSystemConfig, WorkloadSystemConfigAdmin)
admin.site.register(ComponentParam, ComponentParamAdmin)
admin.site.register(ComponentVersion, ComponentVersionAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Workload, WorkloadAdmin)
admin.site.register(ProvisonParameterValue,ProvisonParameterValueAdmin)
admin.site.register(LocalJobTestResult,LocalTestResultAdmin)