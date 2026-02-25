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
    from django.db.models import Q
    
    services = Service.objects.all()
    
    # Búsqueda por nombre o descripción
    search = request.GET.get('search', '')
    if search:
        services = services.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    # Filtro por estado
    status = request.GET.get('status', '')
    if status == 'active':
        services = services.filter(is_active=True)
    elif status == 'inactive':
        services = services.filter(is_active=False)
    
    # Filtro por tipo de facturación
    billing_type = request.GET.get('billing_type', '')
    if billing_type:
        services = services.filter(billing_type=billing_type)
    
    # Filtro por precio mínimo
    min_price = request.GET.get('min_price', '')
    if min_price:
        try:
            services = services.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    
    # Filtro por precio máximo
    max_price = request.GET.get('max_price', '')
    if max_price:
        try:
            services = services.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass
    
    # Ordenamiento
    sort = request.GET.get('sort', 'name')
    if sort == 'price_asc':
        services = services.order_by('price')
    elif sort == 'price_desc':
        services = services.order_by('-price')
    elif sort == 'newest':
        services = services.order_by('-created_at')
    else:
        services = services.order_by('name')
    
    # Obtener valores únicos para los filtros
    billing_types = Service.BILLING_TYPE_CHOICES
    
    return render(request, 'core/dashboard_services_list.html', {
        'object_list': services,
        'search': search,
        'status': status,
        'billing_type': billing_type,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
        'billing_types': billing_types,
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


@login_required
@dashboard_required
def dashboard_quote_pdf(request, pk):
    """Genera PDF de la cotización"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from io import BytesIO
    
    quote = get_object_or_404(Quote, pk=pk)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#dc2626'),
        alignment=TA_CENTER,
        spaceAfter=30,
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=12,
    )
    
    # Encabezado
    elements.append(Paragraph('MEGADOMINIO', title_style))
    elements.append(Paragraph('Soluciones Digitales Profesionales', subtitle_style))
    elements.append(Paragraph('info@megadominio.com | +57 300 123 4567 | Bogota, Colombia', subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del documento
    elements.append(Paragraph(f'COTIZACION #{quote.number}', heading_style))
    elements.append(Paragraph(f'Estado: {quote.get_status_display()}', styles['Normal']))
    elements.append(Paragraph(f'Valida hasta: {quote.valid_until.strftime("%d/%m/%Y")}', styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del cliente
    info_data = [
        ['<b>INFORMACION DEL CLIENTE</b>', '<b>INFORMACION DEL DOCUMENTO</b>'],
        [f'Cliente: {quote.client.name}', f'Fecha: {quote.created_at.strftime("%d/%m/%Y")}'],
        [f'Email: {quote.client.email}', f'Valida hasta: {quote.valid_until.strftime("%d/%m/%Y")}'],
    ]
    
    if quote.client.company:
        info_data.insert(2, [f'Empresa: {quote.client.company}', ''])
    if quote.client.phone:
        info_data.insert(3, [f'Telefono: {quote.client.phone}', ''])
    
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f9fafb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de items
    elements.append(Paragraph('DETALLE DE ITEMS', heading_style))
    
    items_data = [['Servicio', 'Descripcion', 'Cant.', 'Precio Unit.', 'Subtotal']]
    
    for item in quote.items.all():
        desc = item.description[:40] + '...' if len(item.description) > 40 else item.description
        items_data.append([
            item.service.name,
            desc,
            str(item.quantity),
            f'${item.unit_price:,.0f}',
            f'${item.subtotal:,.0f}',
        ])
    
    items_table = Table(items_data, colWidths=[1.8*inch, 2.2*inch, 0.7*inch, 1.3*inch, 1.3*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de totales
    totals_data = [
        ['Subtotal:', f'${quote.subtotal:,.0f} COP'],
        [f'Descuento ({quote.discount_percentage}%):', f'${quote.discount_amount:,.0f} COP'],
        [f'IVA ({quote.tax_percentage}%):', f'${quote.tax_amount:,.0f} COP'],
        ['<b>TOTAL:</b>', f'<b>${quote.total:,.0f} COP</b>'],
    ]
    
    totals_table = Table(totals_data, colWidths=[5*inch, 2.3*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, 2), colors.black),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#dc2626')),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 3), (-1, 3), 14),
        ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#dc2626')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(totals_table)
    
    if quote.notes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph('<b>Notas:</b>', styles['Normal']))
        elements.append(Paragraph(quote.notes, styles['Normal']))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="cotizacion_{quote.number}.pdf"'
    response.write(pdf)
    
    return response


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


@login_required
@dashboard_required
def dashboard_invoice_pdf(request, pk):
    """Genera PDF de la factura"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from io import BytesIO
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#dc2626'),
        alignment=TA_CENTER,
        spaceAfter=30,
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=12,
    )
    
    # Encabezado
    elements.append(Paragraph('MEGADOMINIO', title_style))
    elements.append(Paragraph('Soluciones Digitales Profesionales', subtitle_style))
    elements.append(Paragraph('info@megadominio.com | +57 300 123 4567 | Bogota, Colombia', subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del documento
    elements.append(Paragraph(f'FACTURA #{invoice.number}', heading_style))
    elements.append(Paragraph(f'Estado: {invoice.get_status_display()}', styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del cliente
    info_data = [
        ['<b>INFORMACION DEL CLIENTE</b>', '<b>INFORMACION DEL DOCUMENTO</b>'],
        [f'Cliente: {invoice.client.name}', f'Fecha de Emision: {invoice.issue_date.strftime("%d/%m/%Y")}'],
        [f'Email: {invoice.client.email}', f'Fecha de Vencimiento: {invoice.due_date.strftime("%d/%m/%Y")}'],
    ]
    
    if invoice.client.company:
        info_data.insert(2, [f'Empresa: {invoice.client.company}', ''])
    if invoice.client.phone:
        info_data.insert(3, [f'Telefono: {invoice.client.phone}', ''])
    if invoice.quote:
        info_data.append(['', f'Cotizacion: {invoice.quote.number}'])
    if invoice.paid_date:
        info_data.append(['', f'Fecha de Pago: {invoice.paid_date.strftime("%d/%m/%Y")}'])
    
    info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f9fafb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de items
    elements.append(Paragraph('DETALLE DE ITEMS', heading_style))
    
    items_data = [['Servicio', 'Descripcion', 'Cant.', 'Precio Unit.', 'Subtotal']]
    
    for item in invoice.items.all():
        desc = item.description[:40] + '...' if len(item.description) > 40 else item.description
        items_data.append([
            item.service.name,
            desc,
            str(item.quantity),
            f'${item.unit_price:,.0f}',
            f'${item.subtotal:,.0f}',
        ])
    
    items_table = Table(items_data, colWidths=[1.8*inch, 2.2*inch, 0.7*inch, 1.3*inch, 1.3*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de totales
    totals_data = [
        ['Subtotal:', f'${invoice.subtotal:,.0f} COP'],
        [f'Descuento ({invoice.discount_percentage}%):', f'${invoice.discount_amount:,.0f} COP'],
        [f'IVA ({invoice.tax_percentage}%):', f'${invoice.tax_amount:,.0f} COP'],
        ['<b>TOTAL:</b>', f'<b>${invoice.total:,.0f} COP</b>'],
    ]
    
    totals_table = Table(totals_data, colWidths=[5*inch, 2.3*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, 2), colors.black),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#dc2626')),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 3), (-1, 3), 14),
        ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#dc2626')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(totals_table)
    
    if invoice.notes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph('<b>Notas:</b>', styles['Normal']))
        elements.append(Paragraph(invoice.notes, styles['Normal']))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="factura_{invoice.number}.pdf"'
    response.write(pdf)
    
    return response


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


@login_required
@dashboard_required
def dashboard_cuenta_pdf(request, pk):
    """Genera PDF de la cuenta de cobro con formato limpio."""
    from io import BytesIO
    import os
    from xml.sax.saxutils import escape
    from django.conf import settings
    from django.http import HttpResponse
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    cuenta = get_object_or_404(CuentaDeCobro, pk=pk)

    def format_money(value):
        try:
            return f"${int(value):,}".replace(",", ".")
        except (TypeError, ValueError):
            return "$0"

    def detect_observation_text():
        if cuenta.notes:
            return cuenta.notes

        product_keywords = {
            'procesador', 'cpu', 'ryzen', 'intel', 'core', 'tarjeta', 'madre', 'motherboard',
            'ram', 'ddr', 'ssd', 'hdd', 'nvme', 'm.2', 'fuente', 'psu', 'gabinete', 'chasis',
            'gpu', 'rtx', 'gtx', 'radeon', 'monitor', 'teclado', 'mouse', 'hardware', 'componente',
            'ensamblaje', 'montaje', 'disco'
        }
        service_keywords = {
            'hosting', 'dominio', 'desarrollo', 'diseño', 'web', 'mantenimiento', 'soporte',
            'ssl', 'certificado', 'seo', 'marketing', 'consultoria', 'asesoria',
            'suscripcion', 'mensual', 'anual', 'servicio'
        }

        has_products = False
        has_services = False

        for item in cuenta.items.all():
            text = ((item.description or '') + ' ' + (item.service.name if item.service else '')).lower()
            billing_type = item.service.billing_type if item.service else None

            if billing_type in ('monthly', 'annual'):
                has_services = True
                continue

            is_product = any(word in text for word in product_keywords)
            is_service = any(word in text for word in service_keywords)

            if is_product and not is_service:
                has_products = True
            elif is_service and not is_product:
                has_services = True
            elif billing_type == 'unique':
                has_products = True
            else:
                has_services = True

        if has_products and not has_services:
            return getattr(
                settings,
                'CUENTA_COBRO_OBS_PRODUCTOS',
                'Garantía de montaje 30 días sobre mano de obra. Los componentes tienen garantía del fabricante según cada pieza.'
            )
        if has_services and not has_products:
            return getattr(
                settings,
                'CUENTA_COBRO_OBS_SERVICIOS',
                'Garantía de 30 días sobre el servicio prestado. Soporte técnico incluido durante el período de garantía.'
            )
        return getattr(
            settings,
            'CUENTA_COBRO_OBS_MIXTO',
            'Garantía de 30 días sobre mano de obra y servicios prestados. Los componentes físicos tienen garantía del fabricante según cada pieza.'
        )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
    )
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        'CuentaTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=13.5,
        leading=16,
    )
    date_style = ParagraphStyle(
        'CuentaDate',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=9,
        alignment=2,
    )
    left_info_style = ParagraphStyle(
        'LeftInfo',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
    )
    right_info_style = ParagraphStyle(
        'RightInfo',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
        alignment=2,
    )
    obs_style = ParagraphStyle(
        'Obs',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
    )
    legal_style = ParagraphStyle(
        'Legal',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=9,
        leading=13,
    )
    total_style = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=18,
        alignment=2,
    )

    # Header
    logo_paths = [
        os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png'),
        os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.jpg'),
        os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png'),
        os.path.join(settings.BASE_DIR, 'staticfiles', 'img', 'logo.png'),
    ]
    logo_cell = Paragraph('<b> </b>', styles['Normal'])
    for path in logo_paths:
        if os.path.exists(path):
            try:
                logo = RLImage(path)
                logo.drawHeight = 0.38 * inch
                logo.drawWidth = 0.85 * inch
                logo_cell = logo
                break
            except Exception:
                pass

    header_table = Table(
        [[
            logo_cell,
            Paragraph(f'CUENTA DE COBRO #{escape(str(cuenta.number))}', title_style),
            Paragraph(f'FECHA {cuenta.issue_date.strftime("%d/%m/%Y")}', date_style),
        ]],
        colWidths=[0.85 * inch, 4.1 * inch, 2.0 * inch],
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.34 * inch))

    emisor_nombre = getattr(settings, 'CUENTA_COBRO_EMISOR_NOMBRE', 'CRISTIAN GALLEGO ARBOLEDA')
    emisor_documento = getattr(settings, 'CUENTA_COBRO_EMISOR_DOCUMENTO', 'C.C. 1.036.640.871')
    emisor_direccion = getattr(settings, 'CUENTA_COBRO_EMISOR_DIRECCION', '')
    emisor_ciudad = getattr(settings, 'CUENTA_COBRO_EMISOR_CIUDAD', '')
    emisor_telefono = getattr(settings, 'CUENTA_COBRO_EMISOR_TELEFONO', '')
    emisor_email = getattr(settings, 'CUENTA_COBRO_EMISOR_EMAIL', '')

    doc_type = 'NIT' if cuenta.client.document_type == 'nit' else cuenta.client.get_document_type_display()
    client_name = cuenta.client.company or cuenta.client.name
    client_info_lines = [
        f"<b>{escape(client_name)}</b>",
        f"{escape(doc_type)} {escape(cuenta.client.document_number or '')}",
    ]
    if cuenta.client.address:
        client_info_lines.append(escape(cuenta.client.address))
    if cuenta.client.phone:
        client_info_lines.append(f"Tel: {escape(cuenta.client.phone)}")
    if cuenta.client.email:
        client_info_lines.append(escape(cuenta.client.email))
    client_info_lines.append(f"Estado: {escape(cuenta.get_status_display())}")
    client_info_lines.append(
        f"Vence: {escape(cuenta.due_date.strftime('%d/%m/%Y'))}"
    )
    if cuenta.quote:
        client_info_lines.append(f"Cotización: {escape(cuenta.quote.number)}")

    emisor_lines = [
        f"<b>{escape(emisor_nombre)}</b>",
        escape(emisor_documento),
        escape(emisor_direccion),
        escape(emisor_ciudad),
        f"Tel: {escape(emisor_telefono)}" if emisor_telefono else "",
        f"Email: {escape(emisor_email)}" if emisor_email else "",
    ]

    info_table = Table([[
        Paragraph("<br/>".join([line for line in emisor_lines if line]), left_info_style),
        Paragraph("<br/>".join(client_info_lines), right_info_style),
    ]], colWidths=[3.45 * inch, 3.5 * inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.34 * inch))

    # Items table
    table_data = [["Descripción", "Cantidad", "Valor Unitario", "Subtotal"]]
    for item in cuenta.items.all():
        service_name = item.service.name if item.service else ""
        description = item.description or service_name
        if service_name and item.description and item.description != service_name:
            description = f"{service_name} ({item.description})"
        table_data.append([
            str(description),
            str(int(item.quantity or 0)),
            format_money(item.unit_price),
            format_money(item.subtotal),
        ])

    items_table = Table(
        table_data,
        colWidths=[3.72 * inch, 0.86 * inch, 1.26 * inch, 1.26 * inch],
        repeatRows=1,
    )
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.26 * inch))

    if cuenta.discount_amount or cuenta.tax_amount:
        totals_meta = []
        if cuenta.discount_amount:
            totals_meta.append(
                f"Descuento: {format_money(cuenta.discount_amount)}"
            )
        if cuenta.tax_amount:
            totals_meta.append(
                f"Impuesto ({cuenta.tax_percentage}%): {format_money(cuenta.tax_amount)}"
            )
        meta_text = " | ".join(totals_meta)
        elements.append(Paragraph(escape(meta_text), right_info_style))
        elements.append(Spacer(1, 0.04 * inch))

    elements.append(
        Paragraph(f"TOTAL A PAGAR: {format_money(cuenta.total)}", total_style)
    )
    elements.append(Spacer(1, 0.42 * inch))

    obs_text = detect_observation_text()
    elements.append(Paragraph(f"<b>OBSERVACIONES:</b> {escape(obs_text)}", obs_style))
    elements.append(Spacer(1, 0.42 * inch))

    # Firma: usar imagen si existe; fallback a linea manual
    signature_image = None
    signature_paths = [
        os.path.join(settings.BASE_DIR, 'static', 'img', 'Sin título.jpg'),
        os.path.join(settings.BASE_DIR, 'static', 'img', 'Sin titulo.jpg'),
        os.path.join(settings.BASE_DIR, 'static', 'img', 'firma.jpg'),
        os.path.join(settings.BASE_DIR, 'static', 'img', 'firma.png'),
        os.path.join(settings.BASE_DIR, 'staticfiles', 'img', 'Sin título.jpg'),
    ]
    for path in signature_paths:
        if os.path.exists(path):
            try:
                # Leer bytes evita problemas con rutas con tildes en Windows
                with open(path, 'rb') as sig_file:
                    signature_image = RLImage(BytesIO(sig_file.read()))
                signature_image.drawWidth = 2.35 * inch
                signature_image.drawHeight = 0.62 * inch
                break
            except Exception:
                pass

    if signature_image:
        elements.append(signature_image)
        elements.append(Spacer(1, 0.03 * inch))
    else:
        signature_line = Table([[""]], colWidths=[1.6 * inch], rowHeights=[0.01 * inch])
        signature_line.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (0, 0), 1, colors.black),
        ]))
        elements.append(signature_line)
        elements.append(Spacer(1, 0.08 * inch))
    elements.append(Paragraph(f"<b>{escape(emisor_nombre)}</b><br/>{escape(emisor_documento)}", left_info_style))
    elements.append(Spacer(1, 0.22 * inch))

    legal_text = getattr(
        settings,
        'CUENTA_COBRO_TEXTO_LEGAL',
        'Conforme al parágrafo 2 del art 383 ET, informo que no he sido contratado o vinculado las (2) o más trabajadores asociados a mi actividad. NO PRACTICAR RETENCION EN LA FUENTE.'
    )
    elements.append(Paragraph(escape(legal_text), legal_style))

    doc.build(elements)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="cuenta_cobro_{cuenta.number}.pdf"'
    response.write(buffer.getvalue())
    buffer.close()
    return response


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
