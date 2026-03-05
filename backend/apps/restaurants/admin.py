from django.contrib import admin

# Register your models here.
from .models import Restaurant, Branch, Table

admin.site.register(Restaurant)
admin.site.register(Branch)
admin.site.register(Table)