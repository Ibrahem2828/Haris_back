from django.contrib import admin

from .models import Device, Network, VLAN


admin.site.register(Network)
admin.site.register(VLAN)
admin.site.register(Device)
