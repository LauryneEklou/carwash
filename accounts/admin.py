from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Vehicle

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_employee', 'is_admin')
    list_filter = ('is_staff', 'is_employee', 'is_admin', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_employee', 'is_admin', 'groups', 'user_permissions')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'address'),
        }),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Vehicle)
