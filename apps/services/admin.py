from django.contrib import admin
from .models import Service, ClientService


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'billing_type', 'is_active')
    list_filter = ('billing_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Información de facturación', {
            'fields': ('price', 'billing_type')
        }),
    )


@admin.register(ClientService)
class ClientServiceAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'status', 'start_date', 'monthly_price')
    list_filter = ('status', 'start_date')
    search_fields = ('client__name', 'service__name')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Asignación', {
            'fields': ('client', 'service')
        }),
        ('Estado y fechas', {
            'fields': ('status', 'start_date', 'end_date')
        }),
        ('Información financiera', {
            'fields': ('monthly_price',)
        }),
        ('Información adicional', {
            'fields': ('notes',)
        }),
    )
