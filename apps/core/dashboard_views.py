"""Vistas del dashboard - listados, detalle, crear, editar"""
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from datetime import date

from apps.quotes.models import Quote, QuoteItem
from apps.invoices.models import Invoice, InvoiceItem, CuentaDeCobro, CuentaDeCobroItem
from apps.clients.models import Client
from apps.services.models import Service, ClientService
from apps.store.models import ProductCategory, Product, Order, OrderItem
from .forms import (
    ClientForm, ServiceForm,
    QuoteForm, QuoteItemFormSet,
    InvoiceForm, InvoiceItemFormSet,
    CuentaDeCobroForm, CuentaDeCobroItemFormSet,
    ClientServiceForm,
    UserForm, UserCreateForm,
    ProductCategoryForm, ProductForm,
    OrderForm, OrderItemFormSet,
    HomeClientLogoForm, HomeTestimonialForm,
)
from .models import HomeClientLogo, HomeTestimonial

User = get_user_model()


def dashboard_required(view_func):
    """Decorador que verifica acceso al dashboard"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin and not request.user.is_advisor:
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def _get_next_number(prefix, model_class, number_field='number'):
    """Genera el siguiente número para cotización o cuenta de cobro"""
    from django.db.models import Max
    last = model_class.objects.aggregate(
        max_num=Max(number_field)
    )['max_num']
    if last:
        try:
            num = int(''.join(filter(str.isdigit, str(last)))) + 1
        except (ValueError, TypeError):
            num = 1
    else:
        num = 1
    return f"{prefix}-{num:04d}"


# ============ CLIENTES ============

@login_required
@dashboard_required
def dashboard_clients(request):
    clients = Client.objects.all().order_by('name')
    return render(request, 'core/dashboard_list.html', {
        'object_list': clients,
        'title': 'Clientes',
        'create_url': 'core:dashboard_client_create',
        'detail_url': 'core:dashboard_client_detail',
        'empty_message': 'No hay clientes registrados.',
        'columns': [
            ('name', 'Nombre'),
            ('email', 'Email'),
            ('phone', 'Teléfono'),
            ('company', 'Empresa'),
        ]
    })


@login_required
@dashboard_required
def dashboard_client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client_services = ClientService.objects.filter(
        client=client
    ).select_related('service')
    return render(request, 'core/dashboard_client_detail.html', {
        'client': client,
        'client_services': client_services,
    })


@login_required
@dashboard_required
def dashboard_client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_clients')
    else:
        form = ClientForm()
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': 'Nuevo Cliente',
        'back_url': 'core:dashboard_clients',
    })


@login_required
@dashboard_required
def dashboard_client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_client_detail', pk=pk)
    else:
        form = ClientForm(instance=client)
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': f'Editar Cliente: {client.name}',
        'back_url': 'core:dashboard_client_detail',
        'back_pk': pk,
    })


@login_required
@dashboard_required
def dashboard_client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        return redirect('core:dashboard_clients')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': client,
        'object_name': client.name,
        'title': f'Eliminar cliente: {client.name}',
        'back_url': 'core:dashboard_client_detail',
        'back_pk': pk,
        'list_url': 'core:dashboard_clients',
    })


# ============ SERVICIOS ============

@login_required
@dashboard_required
def dashboard_services(request):
    services = Service.objects.all().order_by('name')
    return render(request, 'core/dashboard_services_list.html', {
        'object_list': services,
    })


@login_required
@dashboard_required
def dashboard_service_toggle(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.is_active = not service.is_active
        service.save(update_fields=['is_active'])
    return redirect('core:dashboard_services')


@login_required
@dashboard_required
def dashboard_service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'core/dashboard_service_detail.html', {
        'service': service,
    })


@login_required
@dashboard_required
def dashboard_service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_services')
    else:
        form = ServiceForm()
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': 'Nuevo Servicio',
        'back_url': 'core:dashboard_services',
    })


@login_required
@dashboard_required
def dashboard_service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_service_detail', pk=pk)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': f'Editar Servicio: {service.name}',
        'back_url': 'core:dashboard_service_detail',
        'back_pk': pk,
    })


@login_required
@dashboard_required
def dashboard_service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('core:dashboard_services')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': service,
        'object_name': service.name,
        'title': f'Eliminar servicio: {service.name}',
        'back_url': 'core:dashboard_service_detail',
        'back_pk': pk,
        'list_url': 'core:dashboard_services',
    })


# ============ COTIZACIONES ============

@login_required
@dashboard_required
def dashboard_quotes(request):
    quotes = Quote.objects.select_related('client').order_by('-created_at')
    return render(request, 'core/dashboard_quotes_list.html', {
        'object_list': quotes,
        'title': 'Cotizaciones',
        'create_url': 'core:dashboard_quote_create',
        'detail_url': 'core:dashboard_quote_detail',
    })


@login_required
@dashboard_required
def dashboard_quote_detail(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    return render(request, 'core/dashboard_quote_detail.html', {'quote': quote})


@login_required
@dashboard_required
def dashboard_quote_create(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        formset = QuoteItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            quote = form.save(commit=False)
            quote.created_by = request.user
            quote.number = _get_next_number('COT', Quote)
            quote.save()
            formset.instance = quote
            formset.save()
            return redirect('core:dashboard_quotes')
    else:
        form = QuoteForm(initial={
            'number': _get_next_number('COT', Quote),
        })
        formset = QuoteItemFormSet()
    return render(request, 'core/dashboard_quote_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Nueva Cotización',
        'back_url': 'core:dashboard_quotes',
    })


@login_required
@dashboard_required
def dashboard_quote_edit(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        form = QuoteForm(request.POST, instance=quote)
        formset = QuoteItemFormSet(request.POST, instance=quote)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('core:dashboard_quote_detail', pk=pk)
    else:
        form = QuoteForm(instance=quote)
        formset = QuoteItemFormSet(instance=quote)
    return render(request, 'core/dashboard_quote_form.html', {
        'form': form,
        'formset': formset,
        'title': f'Editar Cotización: {quote.number}',
        'back_url': 'core:dashboard_quote_detail',
        'back_pk': pk,
    })


@login_required
@dashboard_required
def dashboard_quote_delete(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    if request.method == 'POST':
        quote.delete()
        return redirect('core:dashboard_quotes')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': quote,
        'object_name': quote.number,
        'title': f'Eliminar cotización: {quote.number}',
        'back_url': 'core:dashboard_quote_detail',
        'back_pk': pk,
        'list_url': 'core:dashboard_quotes',
    })


# ============ FACTURAS ============

@login_required
@dashboard_required
def dashboard_invoices(request):
    invoices = Invoice.objects.select_related(
        'client', 'quote'
    ).order_by('-created_at')
    return render(request, 'core/dashboard_invoices_list.html', {
        'object_list': invoices,
        'title': 'Facturas',
    })


@login_required
@dashboard_required
def dashboard_invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'core/dashboard_invoice_detail.html', {
        'invoice': invoice,
    })


@login_required
@dashboard_required
def dashboard_invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.number = _get_next_number('INV', Invoice)
            invoice.save()
            formset.instance = invoice
            formset.save()
            return redirect('core:dashboard_invoices')
    else:
        form = InvoiceForm(initial={
            'issue_date': date.today(),
            'due_date': date.today(),
        })
        formset = InvoiceItemFormSet()
    return render(request, 'core/dashboard_invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Nueva Factura',
        'back_url': 'core:dashboard_invoices',
    })


@login_required
@dashboard_required
def dashboard_invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('core:dashboard_invoice_detail', pk=pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)
    return render(request, 'core/dashboard_invoice_form.html', {
        'form': form,
        'formset': formset,
        'title': f'Editar Factura: {invoice.number}',
        'back_url': 'core:dashboard_invoice_detail',
        'back_pk': pk,
    })


@login_required
@dashboard_required
def dashboard_invoice_mark_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.mark_as_paid()
    return redirect('core:dashboard_invoice_detail', pk=pk)


@login_required
@dashboard_required
def dashboard_invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        return redirect('core:dashboard_invoices')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': invoice,
        'object_name': invoice.number,
        'title': f'Eliminar factura: {invoice.number}',
        'back_url': 'core:dashboard_invoice_detail',
        'back_pk': pk,
        'list_url': 'core:dashboard_invoices',
    })


# ============ CUENTAS DE COBRO ============

@login_required
@dashboard_required
def dashboard_cuentas_cobro(request):
    cuentas = CuentaDeCobro.objects.select_related(
        'client'
    ).order_by('-created_at')
    return render(request, 'core/dashboard_cuentas_list.html', {
        'object_list': cuentas,
        'title': 'Cuentas de cobro',
        'create_url': 'core:dashboard_cuenta_create',
        'detail_url': 'core:dashboard_cuenta_detail',
    })


@login_required
@dashboard_required
def dashboard_cuenta_detail(request, pk):
    cuenta = get_object_or_404(CuentaDeCobro, pk=pk)
    return render(request, 'core/dashboard_cuenta_detail.html', {
        'cuenta': cuenta,
    })


@login_required
@dashboard_required
def dashboard_cuenta_create(request):
    if request.method == 'POST':
        form = CuentaDeCobroForm(request.POST)
        formset = CuentaDeCobroItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            cuenta = form.save(commit=False)
            cuenta.created_by = request.user
            cuenta.number = _get_next_number('CC', CuentaDeCobro)
            cuenta.issue_date = cuenta.issue_date or date.today()
            cuenta.due_date = cuenta.due_date or date.today()
            cuenta.save()
            formset.instance = cuenta
            formset.save()
            cuenta.calculate_totals()
            return redirect('core:dashboard_cuentas_cobro')
    else:
        form = CuentaDeCobroForm(initial={
            'number': _get_next_number('CC', CuentaDeCobro),
            'issue_date': date.today(),
            'due_date': date.today(),
        })
        formset = CuentaDeCobroItemFormSet()
    return render(request, 'core/dashboard_cuenta_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Nueva Cuenta de cobro',
        'back_url': 'core:dashboard_cuentas_cobro',
    })


@login_required
@dashboard_required
def dashboard_cuenta_edit(request, pk):
    cuenta = get_object_or_404(CuentaDeCobro, pk=pk)
    if request.method == 'POST':
        form = CuentaDeCobroForm(request.POST, instance=cuenta)
        formset = CuentaDeCobroItemFormSet(request.POST, instance=cuenta)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            cuenta.calculate_totals()
            return redirect('core:dashboard_cuenta_detail', pk=pk)
    else:
        form = CuentaDeCobroForm(instance=cuenta)
        formset = CuentaDeCobroItemFormSet(instance=cuenta)
    return render(request, 'core/dashboard_cuenta_form.html', {
        'form': form,
        'formset': formset,
        'title': f'Editar Cuenta de cobro: {cuenta.number}',
        'back_url': 'core:dashboard_cuenta_detail',
        'back_pk': pk,
    })


@login_required
@dashboard_required
def dashboard_cuenta_mark_paid(request, pk):
    cuenta = get_object_or_404(CuentaDeCobro, pk=pk)
    cuenta.mark_as_paid()
    return redirect('core:dashboard_cuenta_detail', pk=pk)


@login_required
@dashboard_required
def dashboard_cuenta_delete(request, pk):
    cuenta = get_object_or_404(CuentaDeCobro, pk=pk)
    if request.method == 'POST':
        cuenta.delete()
        return redirect('core:dashboard_cuentas_cobro')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': cuenta,
        'object_name': cuenta.number,
        'title': f'Eliminar cuenta de cobro: {cuenta.number}',
        'back_url': 'core:dashboard_cuenta_detail',
        'back_pk': pk,
        'list_url': 'core:dashboard_cuentas_cobro',
    })


# ============ SERVICIOS DE CLIENTES ============

@login_required
@dashboard_required
def dashboard_client_services(request):
    cs_list = ClientService.objects.select_related(
        'client', 'service'
    ).order_by('-created_at')
    return render(request, 'core/dashboard_client_services_list.html', {
        'object_list': cs_list,
        'title': 'Servicios de clientes',
    })


@login_required
@dashboard_required
def dashboard_client_service_detail(request, pk):
    cs = get_object_or_404(
        ClientService.objects.select_related('client', 'service'), pk=pk
    )
    return render(request, 'core/dashboard_client_service_detail.html', {
        'cs': cs,
    })


@login_required
@dashboard_required
def dashboard_client_service_create(request):
    if request.method == 'POST':
        form = ClientServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_client_services')
    else:
        form = ClientServiceForm()
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': 'Asignar servicio a cliente',
        'back_url': 'core:dashboard_client_services',
    })


@login_required
@dashboard_required
def dashboard_client_service_edit(request, pk):
    cs = get_object_or_404(ClientService, pk=pk)
    if request.method == 'POST':
        form = ClientServiceForm(request.POST, instance=cs)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_client_service_detail', pk=pk)
    else:
        form = ClientServiceForm(instance=cs)
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': f'Editar: {cs}',
        'back_url': 'core:dashboard_client_service_detail',
        'back_pk': pk,
    })


@login_required
@dashboard_required
def dashboard_client_service_delete(request, pk):
    cs = get_object_or_404(ClientService, pk=pk)
    if request.method == 'POST':
        cs.delete()
        return redirect('core:dashboard_client_services')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': cs,
        'object_name': str(cs),
        'title': f'Eliminar asignación: {cs}',
        'back_url': 'core:dashboard_client_service_detail',
        'back_pk': pk,
        'list_url': 'core:dashboard_client_services',
    })


# ============ USUARIOS ============

@login_required
@dashboard_required
def dashboard_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'core/dashboard_users_list.html', {
        'object_list': users,
        'title': 'Usuarios',
    })


@login_required
@dashboard_required
def dashboard_user_detail(request, pk):
    u = get_object_or_404(User, pk=pk)
    return render(request, 'core/dashboard_user_detail.html', {'u': u})


@login_required
@dashboard_required
def dashboard_user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_users')
    else:
        form = UserCreateForm()
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': 'Nuevo Usuario',
        'back_url': 'core:dashboard_users',
    })


@login_required
@dashboard_required
def dashboard_user_edit(request, pk):
    u = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_user_detail', pk=pk)
    else:
        form = UserForm(instance=u)
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': f'Editar Usuario: {u}',
        'back_url': 'core:dashboard_user_detail',
        'back_pk': pk,
    })


# ============ PRODUCTOS (TIENDA) ============

@login_required
@dashboard_required
def dashboard_products(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    return render(request, 'core/dashboard_products_list.html', {
        'object_list': products,
        'title': 'Productos',
    })


@login_required
@dashboard_required
def dashboard_product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category'), pk=pk
    )
    return render(request, 'core/dashboard_product_detail.html', {
        'product': product,
    })


@login_required
@dashboard_required
def dashboard_product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_products')
    else:
        form = ProductForm()
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': 'Nuevo Producto',
        'back_url': 'core:dashboard_products',
    })


@login_required
@dashboard_required
def dashboard_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': f'Editar Producto: {product.name}',
        'back_url': 'core:dashboard_product_detail',
        'back_pk': pk,
    })


@login_required
@dashboard_required
def dashboard_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('core:dashboard_products')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': product,
        'object_name': product.name,
        'title': f'Eliminar producto: {product.name}',
        'back_url': 'core:dashboard_product_detail',
        'back_pk': pk,
        'list_url': 'core:dashboard_products',
    })


# ============ CATEGORÍAS DE PRODUCTOS ============

@login_required
@dashboard_required
def dashboard_product_categories(request):
    categories = ProductCategory.objects.annotate(
        product_count=Count('products')
    ).order_by('order', 'name')
    return render(request, 'core/dashboard_product_categories_list.html', {
        'object_list': categories,
        'title': 'Categorías de productos',
    })


@login_required
@dashboard_required
def dashboard_product_category_create(request):
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_product_categories')
    else:
        form = ProductCategoryForm()
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': 'Nueva Categoría',
        'back_url': 'core:dashboard_product_categories',
    })


@login_required
@dashboard_required
def dashboard_product_category_edit(request, pk):
    cat = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_product_categories')
    else:
        form = ProductCategoryForm(instance=cat)
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': f'Editar Categoría: {cat.name}',
        'back_url': 'core:dashboard_product_categories',
    })


@login_required
@dashboard_required
def dashboard_product_category_delete(request, pk):
    cat = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        cat.delete()
        return redirect('core:dashboard_product_categories')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': cat,
        'object_name': cat.name,
        'title': f'Eliminar categoría: {cat.name}',
        'list_url': 'core:dashboard_product_categories',
    })


# ============ ÓRDENES (TIENDA) ============

@login_required
@dashboard_required
def dashboard_orders(request):
    orders = Order.objects.order_by('-created_at')
    return render(request, 'core/dashboard_orders_list.html', {
        'object_list': orders,
        'title': 'Órdenes',
    })


@login_required
@dashboard_required
def dashboard_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'core/dashboard_order_detail.html', {
        'order': order,
    })


@login_required
@dashboard_required
def dashboard_order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            # Procesar el cliente seleccionado
            client = form.cleaned_data.get('client')
            order = form.save(commit=False)
            order.created_by = request.user
            
            # Si se seleccionó un cliente registrado, usar sus datos
            if client:
                order.customer_name = client.name
                order.customer_email = client.email
                order.customer_phone = client.phone
                order.customer_address = client.address
            
            order.save()
            
            # Guardar los items (productos y servicios)
            formset.instance = order
            formset.save()
            
            # Recalcular totales
            order.calculate_totals()
            return redirect('core:dashboard_orders')
    else:
        form = OrderForm(initial={
            'number': _get_next_number('ORD', Order),
        })
        formset = OrderItemFormSet()
    
    # Obtener productos y servicios para el formulario
    products = Product.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)
    
    return render(request, 'core/dashboard_order_form.html', {
        'form': form,
        'formset': formset,
        'products': products,
        'services': services,
        'title': 'Nueva Orden',
        'back_url': 'core:dashboard_orders',
    })


@login_required
@dashboard_required
def dashboard_order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            order.calculate_totals()
            return redirect('core:dashboard_order_detail', pk=pk)


# ============ HOME: LOGOS DE CLIENTES ============

@login_required
@dashboard_required
def dashboard_home_logos(request):
    logos = HomeClientLogo.objects.all().order_by('order', 'name')
    return render(request, 'core/dashboard_list.html', {
        'object_list': logos,
        'title': 'Logos (Home)',
        'create_url': 'core:dashboard_home_logo_create',
        'detail_url': 'core:dashboard_home_logo_edit',
        'empty_message': 'No hay logos registrados.',
        'columns': [
            ('name', 'Nombre'),
            ('order', 'Orden'),
            ('is_active', 'Activo'),
        ],
    })


@login_required
@dashboard_required
def dashboard_home_logo_create(request):
    if request.method == 'POST':
        form = HomeClientLogoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_home_logos')
    else:
        form = HomeClientLogoForm()
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': 'Nuevo logo (Home)',
        'back_url': 'core:dashboard_home_logos',
    })


@login_required
@dashboard_required
def dashboard_home_logo_edit(request, pk):
    logo = get_object_or_404(HomeClientLogo, pk=pk)
    if request.method == 'POST':
        form = HomeClientLogoForm(request.POST, request.FILES, instance=logo)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_home_logos')
    else:
        form = HomeClientLogoForm(instance=logo)
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': f'Editar logo: {logo.name}',
        'back_url': 'core:dashboard_home_logos',
    })


@login_required
@dashboard_required
def dashboard_home_logo_delete(request, pk):
    logo = get_object_or_404(HomeClientLogo, pk=pk)
    if request.method == 'POST':
        logo.delete()
        return redirect('core:dashboard_home_logos')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': logo,
        'object_name': logo.name,
        'title': f'Eliminar logo: {logo.name}',
        'list_url': 'core:dashboard_home_logos',
    })


# ============ HOME: TESTIMONIOS ============

@login_required
@dashboard_required
def dashboard_home_testimonials(request):
    testimonials = HomeTestimonial.objects.all().order_by('order', '-created_at')
    return render(request, 'core/dashboard_list.html', {
        'object_list': testimonials,
        'title': 'Testimonios (Home)',
        'create_url': 'core:dashboard_home_testimonial_create',
        'detail_url': 'core:dashboard_home_testimonial_edit',
        'empty_message': 'No hay testimonios registrados.',
        'columns': [
            ('name', 'Nombre'),
            ('company', 'Empresa'),
            ('rating', 'Rating'),
            ('order', 'Orden'),
            ('is_active', 'Activo'),
        ],
    })


@login_required
@dashboard_required
def dashboard_home_testimonial_create(request):
    if request.method == 'POST':
        form = HomeTestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_home_testimonials')
    else:
        form = HomeTestimonialForm()
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': 'Nuevo testimonio (Home)',
        'back_url': 'core:dashboard_home_testimonials',
    })


@login_required
@dashboard_required
def dashboard_home_testimonial_edit(request, pk):
    t = get_object_or_404(HomeTestimonial, pk=pk)
    if request.method == 'POST':
        form = HomeTestimonialForm(request.POST, request.FILES, instance=t)
        if form.is_valid():
            form.save()
            return redirect('core:dashboard_home_testimonials')
    else:
        form = HomeTestimonialForm(instance=t)
    return render(request, 'core/dashboard_form.html', {
        'form': form,
        'title': f'Editar testimonio: {t.name}',
        'back_url': 'core:dashboard_home_testimonials',
    })


@login_required
@dashboard_required
def dashboard_home_testimonial_delete(request, pk):
    t = get_object_or_404(HomeTestimonial, pk=pk)
    if request.method == 'POST':
        t.delete()
        return redirect('core:dashboard_home_testimonials')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': t,
        'object_name': t.name,
        'title': f'Eliminar testimonio: {t.name}',
        'list_url': 'core:dashboard_home_testimonials',
    })


@login_required
@dashboard_required
def dashboard_order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('core:dashboard_orders')
    return render(request, 'core/dashboard_confirm_delete.html', {
        'object': order,
        'object_name': order.number,
        'title': f'Eliminar orden: {order.number}',
        'back_url': 'core:dashboard_order_detail',
        'back_pk': pk,
        'list_url': 'core:dashboard_orders',
    })


@login_required
@dashboard_required
def dashboard_order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    if new_status and new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save(update_fields=['status'])
    return redirect('core:dashboard_order_detail', pk=pk)
