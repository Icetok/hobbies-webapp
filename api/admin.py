from django.contrib import admin
from .models import CustomUser, Hobby

# Inline for the Hobby relationship in the User model
class UserHobbyInline(admin.TabularInline):
    model = CustomUser.hobbies.through  # Through model for the ManyToManyField
    extra = 1  # Number of empty forms to show by default

# Admin for the CustomUser model
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'name', 'date_of_birth', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    inlines = [UserHobbyInline]  # Add inline for hobbies

# Admin for the Hobby model
class HobbyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# Register the models
admin.site.register(CustomUser, CustomUserAdmin)  # Register CustomUser with its custom admin
admin.site.register(Hobby, HobbyAdmin)  # Register Hobby with its custom admin

 # Username : admin
 # Password: admin

