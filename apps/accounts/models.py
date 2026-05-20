from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        NETWORK_ADMIN = "NETWORK_ADMIN", "Network Admin"
        SECURITY_ENGINEER = "SECURITY_ENGINEER", "Security Engineer"
        STUDENT = "STUDENT", "Student"
        VIEWER = "VIEWER", "Viewer"

    role = models.CharField(max_length=32, choices=Roles.choices, default=Roles.VIEWER)

    @property
    def is_staff_or_admin_role(self):
        return self.is_staff or self.role == self.Roles.ADMIN
