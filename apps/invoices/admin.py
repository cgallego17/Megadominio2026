from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ('service', 'description', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('subtotal',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'status', 'total', 'due_date', 'created_by')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('number', 'client__name', 'client__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('number', 'subtotal', 'tax_amount', 'total')
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        ('Información básica', {
            'fields': ('number', 'client', 'created_by', 'status')
        }),
        ('Fechas', {
            'fields': ('issue_date', 'due_date', 'paid_date')
        }),
        ('Información financiera', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total')
        }),
        ('Información adicional', {
            'fields': ('notes',)
        }),
    )
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = "Marcar como pagadas"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'service', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('service',)
    search_fields = ('invoice__number', 'service__name', 'description')
    readonly_fields = ('subtotal',)
