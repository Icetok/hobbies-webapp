from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Hobby

class CustomUserAdmin(UserAdmin):
    # Add hobbies to the fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('name', 'date_of_birth', 'hobbies')}),
    )
    
    # Add hobbies to the list display
    list_display = ('username', 'email', 'name', 'date_of_birth', 'is_staff')
    
    # Add filter for hobbies
    list_filter = UserAdmin.list_filter + ('hobbies',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Hobby)