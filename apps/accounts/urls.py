from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import HarisTokenObtainPairView, MeView


urlpatterns = [
    path("login/", HarisTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
]
