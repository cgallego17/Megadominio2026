from django.contrib import admin
from django.utils.html import format_html
from .models import Quote, QuoteItem


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    fields = ('service', 'description', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('subtotal',)


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'status', 'total', 'valid_until', 'created_by')
    list_filter = ('status', 'created_at', 'valid_until')
    search_fields = ('number', 'client__name', 'client__email')
    date_hierarchy = 'created_at'
    readonly_fields = ('number', 'subtotal', 'tax_amount', 'total')
    inlines = [QuoteItemInline]
    
    fieldsets = (
        ('Información básica', {
            'fields': ('number', 'client', 'created_by', 'status')
        }),
        ('Fechas', {
            'fields': ('valid_until',)
        }),
        ('Información financiera', {
            'fields': ('subtotal', 'discount_percentage', 'discount_amount', 
                      'tax_percentage', 'tax_amount', 'total')
        }),
        ('Información adicional', {
            'fields': ('notes',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(QuoteItem)
class QuoteItemAdmin(admin.ModelAdmin):
    list_display = ('quote', 'service', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('service', 'quote__status')
    search_fields = ('quote__number', 'service__name', 'description')
    readonly_fields = ('subtotal',)
