from django.contrib import admin
from .models import ProductCategory, Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'badge',
                    'is_active', 'is_featured']
    list_filter = ['category', 'is_active', 'is_featured', 'badge']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer_name', 'status', 'total',
                    'created_at']
    list_filter = ['status']
    search_fields = ['number', 'customer_name', 'customer_email']
    inlines = [OrderItemInline]
