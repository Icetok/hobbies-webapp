from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Hobby

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Hobby)