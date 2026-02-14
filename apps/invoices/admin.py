from django.contrib import admin
from .models import Invoice, InvoiceItem, CuentaDeCobro, CuentaDeCobroItem


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


class CuentaDeCobroItemInline(admin.TabularInline):
    model = CuentaDeCobroItem
    extra = 1
    fields = ('service', 'description', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('subtotal',)


@admin.register(CuentaDeCobro)
class CuentaDeCobroAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'status', 'total', 'due_date', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('number', 'client__name', 'client__email')
    date_hierarchy = 'created_at'
    inlines = [CuentaDeCobroItemInline]
    
    fieldsets = (
        ('Información básica', {
            'fields': ('number', 'client', 'created_by', 'quote', 'status')
        }),
        ('Fechas', {
            'fields': ('issue_date', 'due_date', 'paid_date')
        }),
        ('Información financiera', {
            'fields': ('subtotal', 'discount_amount', 'tax_percentage', 'tax_amount', 'total')
        }),
        ('Información adicional', {
            'fields': ('notes',)
        }),
    )
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        for obj in queryset:
            obj.mark_as_paid()
    mark_as_paid.short_description = "Marcar como pagadas"


@admin.register(CuentaDeCobroItem)
class CuentaDeCobroItemAdmin(admin.ModelAdmin):
    list_display = ('cuenta_de_cobro', 'description', 'service', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('service',)
    search_fields = ('cuenta_de_cobro__number', 'description', 'service__name')
    readonly_fields = ('subtotal',)
