from django.urls import path
from . import views
from . import dashboard_views
from . import panel_views as pv

app_name = 'core'

dv = dashboard_views

urlpatterns = [
    # ── Sitio público ──
    path('', views.home, name='home'),
    path('servicios/', views.services, name='services'),
    path('servicios/<slug:slug>/', views.service_detail, name='service_detail'),
    path('cotizar/', views.quote_request, name='quote_request'),
    path('cotizar/<int:service_id>/', views.quote_request, name='quote_request_service'),
    path('cotizacion-enviada/<int:quote_id>/', views.quote_success, name='quote_success'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('tienda/', views.store, name='store'),
    path('tienda/<slug:slug>/', views.product_detail, name='product_detail'),
    path('coffee/', views.coffee, name='coffee'),
    path('terminos/', views.terms, name='terms'),
    path('privacidad/', views.privacy, name='privacy'),

    # ── Dashboard principal ──
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── Clientes CRUD ──
    path('dashboard/clientes/', dv.dashboard_clients, name='dashboard_clients'),
    path('dashboard/clientes/nuevo/', dv.dashboard_client_create, name='dashboard_client_create'),
    path('dashboard/clientes/<int:pk>/', dv.dashboard_client_detail, name='dashboard_client_detail'),
    path('dashboard/clientes/<int:pk>/editar/', dv.dashboard_client_edit, name='dashboard_client_edit'),
    path('dashboard/clientes/<int:pk>/eliminar/', dv.dashboard_client_delete, name='dashboard_client_delete'),

    # ── Servicios CRUD ──
    path('dashboard/servicios/', dv.dashboard_services, name='dashboard_services'),
    path('dashboard/servicios/nuevo/', dv.dashboard_service_create, name='dashboard_service_create'),
    path('dashboard/servicios/<int:pk>/', dv.dashboard_service_detail, name='dashboard_service_detail'),
    path('dashboard/servicios/<int:pk>/editar/', dv.dashboard_service_edit, name='dashboard_service_edit'),
    path('dashboard/servicios/<int:pk>/eliminar/', dv.dashboard_service_delete, name='dashboard_service_delete'),
    path('dashboard/servicios/<int:pk>/toggle/', dv.dashboard_service_toggle, name='dashboard_service_toggle'),

    # ── Cotizaciones CRUD ──
    path('dashboard/cotizaciones/', dv.dashboard_quotes, name='dashboard_quotes'),
    path('dashboard/cotizaciones/nuevo/', dv.dashboard_quote_create, name='dashboard_quote_create'),
    path('dashboard/cotizaciones/<int:pk>/', dv.dashboard_quote_detail, name='dashboard_quote_detail'),
    path('dashboard/cotizaciones/<int:pk>/editar/', dv.dashboard_quote_edit, name='dashboard_quote_edit'),
    path('dashboard/cotizaciones/<int:pk>/eliminar/', dv.dashboard_quote_delete, name='dashboard_quote_delete'),

    # ── Facturas CRUD ──
    path('dashboard/facturas/', dv.dashboard_invoices, name='dashboard_invoices'),
    path('dashboard/facturas/nuevo/', dv.dashboard_invoice_create, name='dashboard_invoice_create'),
    path('dashboard/facturas/<int:pk>/', dv.dashboard_invoice_detail, name='dashboard_invoice_detail'),
    path('dashboard/facturas/<int:pk>/editar/', dv.dashboard_invoice_edit, name='dashboard_invoice_edit'),
    path('dashboard/facturas/<int:pk>/eliminar/', dv.dashboard_invoice_delete, name='dashboard_invoice_delete'),
    path('dashboard/facturas/<int:pk>/marcar-pagada/', dv.dashboard_invoice_mark_paid, name='dashboard_invoice_mark_paid'),

    # ── Cuentas de cobro CRUD ──
    path('dashboard/cuentas-cobro/', dv.dashboard_cuentas_cobro, name='dashboard_cuentas_cobro'),
    path('dashboard/cuentas-cobro/nuevo/', dv.dashboard_cuenta_create, name='dashboard_cuenta_create'),
    path('dashboard/cuentas-cobro/<int:pk>/', dv.dashboard_cuenta_detail, name='dashboard_cuenta_detail'),
    path('dashboard/cuentas-cobro/<int:pk>/editar/', dv.dashboard_cuenta_edit, name='dashboard_cuenta_edit'),
    path('dashboard/cuentas-cobro/<int:pk>/eliminar/', dv.dashboard_cuenta_delete, name='dashboard_cuenta_delete'),
    path('dashboard/cuentas-cobro/<int:pk>/marcar-pagada/', dv.dashboard_cuenta_mark_paid, name='dashboard_cuenta_mark_paid'),

    # ── Servicios de clientes CRUD ──
    path('dashboard/servicios-clientes/', dv.dashboard_client_services, name='dashboard_client_services'),
    path('dashboard/servicios-clientes/nuevo/', dv.dashboard_client_service_create, name='dashboard_client_service_create'),
    path('dashboard/servicios-clientes/<int:pk>/', dv.dashboard_client_service_detail, name='dashboard_client_service_detail'),
    path('dashboard/servicios-clientes/<int:pk>/editar/', dv.dashboard_client_service_edit, name='dashboard_client_service_edit'),
    path('dashboard/servicios-clientes/<int:pk>/eliminar/', dv.dashboard_client_service_delete, name='dashboard_client_service_delete'),

    # ── Usuarios CRUD ──
    path('dashboard/usuarios/', dv.dashboard_users, name='dashboard_users'),
    path('dashboard/usuarios/nuevo/', dv.dashboard_user_create, name='dashboard_user_create'),
    path('dashboard/usuarios/<int:pk>/', dv.dashboard_user_detail, name='dashboard_user_detail'),
    path('dashboard/usuarios/<int:pk>/editar/', dv.dashboard_user_edit, name='dashboard_user_edit'),

    # ── Productos (Tienda) CRUD ──
    path('dashboard/productos/', dv.dashboard_products, name='dashboard_products'),
    path('dashboard/productos/nuevo/', dv.dashboard_product_create, name='dashboard_product_create'),
    path('dashboard/productos/<int:pk>/', dv.dashboard_product_detail, name='dashboard_product_detail'),
    path('dashboard/productos/<int:pk>/editar/', dv.dashboard_product_edit, name='dashboard_product_edit'),
    path('dashboard/productos/<int:pk>/eliminar/', dv.dashboard_product_delete, name='dashboard_product_delete'),

    # ── Categorías de productos CRUD ──
    path('dashboard/productos/categorias/', dv.dashboard_product_categories, name='dashboard_product_categories'),
    path('dashboard/productos/categorias/nuevo/', dv.dashboard_product_category_create, name='dashboard_product_category_create'),
    path('dashboard/productos/categorias/<int:pk>/editar/', dv.dashboard_product_category_edit, name='dashboard_product_category_edit'),
    path('dashboard/productos/categorias/<int:pk>/eliminar/', dv.dashboard_product_category_delete, name='dashboard_product_category_delete'),

    # ── Órdenes (Tienda) CRUD ──
    path('dashboard/ordenes/', dv.dashboard_orders, name='dashboard_orders'),
    path('dashboard/ordenes/nuevo/', dv.dashboard_order_create, name='dashboard_order_create'),
    path('dashboard/ordenes/<int:pk>/', dv.dashboard_order_detail, name='dashboard_order_detail'),
    path('dashboard/ordenes/<int:pk>/editar/', dv.dashboard_order_edit, name='dashboard_order_edit'),
    path('dashboard/ordenes/<int:pk>/eliminar/', dv.dashboard_order_delete, name='dashboard_order_delete'),
    path('dashboard/ordenes/<int:pk>/estado/', dv.dashboard_order_update_status, name='dashboard_order_update_status'),

    # ── Panel de usuario (Mi Cuenta) ──
    path('mi-cuenta/', pv.panel_home, name='panel_home'),
    path('mi-cuenta/servicios/', pv.panel_servicios, name='panel_servicios'),
    path('mi-cuenta/compras/', pv.panel_compras, name='panel_compras'),
    path('mi-cuenta/compras/<int:pk>/', pv.panel_compra_detail, name='panel_compra_detail'),
    path('mi-cuenta/perfil/', pv.panel_perfil, name='panel_perfil'),
    path('mi-cuenta/perfil/password/', pv.panel_password, name='panel_password'),
    path('mi-cuenta/direcciones/', pv.panel_direcciones, name='panel_direcciones'),
    path('mi-cuenta/direcciones/<int:pk>/editar/', pv.panel_direccion_edit, name='panel_direccion_edit'),
    path('mi-cuenta/direcciones/<int:pk>/eliminar/', pv.panel_direccion_delete, name='panel_direccion_delete'),
    path('mi-cuenta/direcciones/<int:pk>/principal/', pv.panel_direccion_default, name='panel_direccion_default'),

    # ── API geo ──
    path('api/states/', pv.api_states, name='api_states'),
    path('api/cities/', pv.api_cities, name='api_cities'),
]
