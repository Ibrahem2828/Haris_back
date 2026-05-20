from django.contrib import admin

from .models import DetectionJob, DetectionRule


admin.site.register(DetectionRule)
admin.site.register(DetectionJob)
