from django.contrib import admin

# Register your models here.
from .models import OrderSession,OrderItem

admin.site.register(OrderSession)
admin.site.register(OrderItem)