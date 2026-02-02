from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        ('Permisos', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined', 'is_verified')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'timezone', 'language', 'email_notifications')
    list_filter = ('timezone', 'language', 'email_notifications')
    search_fields = ('user__username', 'user__email')
