from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import GeneratePreviewView, ResponseActionViewSet


router = DefaultRouter()
router.register("actions", ResponseActionViewSet, basename="response-action")

urlpatterns = [
    path("generate-preview/", GeneratePreviewView.as_view(), name="response-generate-preview"),
] + router.urls
