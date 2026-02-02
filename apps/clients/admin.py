from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company', 'is_active')
    list_filter = ('is_active', 'document_type')
    search_fields = ('name', 'email', 'company')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'email', 'phone', 'is_active')
        }),
        ('Información de documento', {
            'fields': ('document_type', 'document_number')
        }),
        ('Información de empresa', {
            'fields': ('company', 'address')
        }),
    )
