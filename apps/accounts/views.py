from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.services import audit_log

from .serializers import UserSerializer


class HarisTokenObtainPairView(TokenObtainPairView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        examples=[
            OpenApiExample(
                "Login",
                value={"username": "admin", "password": "change-me"},
                request_only=True,
            ),
            OpenApiExample(
                "JWT pair",
                value={"access": "<jwt-access-token>", "refresh": "<jwt-refresh-token>"},
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = None
        if response.status_code == 200:
            from django.contrib.auth import get_user_model

            user = get_user_model().objects.filter(username=request.data.get("username")).first()
        audit_log(user, "login", "User", user.id if user else None, request, {"username": request.data.get("username"), "success": response.status_code == 200})
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["auth"], responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user).data)
