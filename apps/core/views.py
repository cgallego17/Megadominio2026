from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from apps.quotes.models import Quote, QuoteItem
from apps.invoices.models import Invoice
from apps.clients.models import Client
from apps.services.models import Service, ClientService
from apps.accounts.models import User
from apps.store.models import Product, ProductCategory


def home(request):
    """
    Vista principal del sitio - Home comercial
    """
    # Servicios top por nombre (si existen en BD)
    top_names = {
        'desarrollo_web': 'Desarrollo Web',
        'marketing_digital': 'Marketing Digital',
        'seo': 'SEO / Posicionamiento',
        'branding': 'Diseño Gráfico / Branding',
        'automatizacion': 'Automatización de Procesos',
        'consultoria': 'Consultoría Digital',
    }
    top_services = {}
    for key, name in top_names.items():
        svc = Service.objects.filter(name=name, is_active=True).first()
        if svc:
            top_services[key] = svc

    context = {
        'services': Service.objects.filter(is_active=True)[:6],
        'top_services': top_services,
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    """
    Dashboard administrativo con métricas principales
    """
    if not request.user.is_admin and not request.user.is_advisor:
        return redirect('core:home')
    
    # Métricas generales
    total_quotes = Quote.objects.count()
    total_clients = Client.objects.count()
    total_services = Service.objects.filter(is_active=True).count()
    total_invoices = Invoice.objects.count()
    
    # Cotizaciones por estado (con etiquetas para el template)
    quotes_status_data = Quote.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    quote_status_labels = dict(Quote.STATUS_CHOICES)
    quotes_by_status = [
        {**item, 'status_display': quote_status_labels.get(item['status'], item['status'])}
        for item in quotes_status_data
    ]
    
    # Facturas por estado (con etiquetas para el template)
    invoices_status_data = Invoice.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    invoice_status_labels = dict(Invoice.STATUS_CHOICES)
    invoices_by_status = [
        {**item, 'status_display': invoice_status_labels.get(item['status'], item['status'])}
        for item in invoices_status_data
    ]
    
    # Cotizaciones recientes
    recent_quotes = Quote.objects.select_related('client').order_by(
        '-created_at'
    )[:5]
    
    # Facturas pendientes
    pending_invoices = Invoice.objects.filter(
        status='pending'
    ).select_related('client').order_by('due_date')[:5]
    
    # Servicios más solicitados
    popular_services = Service.objects.annotate(
        quote_count=Count('quoteitem')
    ).order_by('-quote_count')[:5]
    
    # Ingresos del último mes
    one_month_ago = timezone.now() - timedelta(days=30)
    monthly_revenue = Invoice.objects.filter(
        status='paid',
        paid_date__gte=one_month_ago
    ).aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'total_quotes': total_quotes,
        'total_clients': total_clients,
        'total_services': total_services,
        'total_invoices': total_invoices,
        'quotes_by_status': quotes_by_status,
        'invoices_by_status': invoices_by_status,
        'recent_quotes': recent_quotes,
        'pending_invoices': pending_invoices,
        'popular_services': popular_services,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'core/dashboard.html', context)


def about(request):
    """
    Página sobre nosotros
    """
    return render(request, 'core/about.html')


def contact(request):
    """
    Página de contacto
    """
    return render(request, 'core/contact.html')


def store(request):
    """
    Página de la tienda
    """
    products = Product.objects.filter(
        is_active=True
    ).select_related('category').order_by('-is_featured', '-created_at')
    categories = ProductCategory.objects.filter(
        is_active=True
    ).order_by('order', 'name')
    return render(request, 'core/store.html', {
        'products': products,
        'categories': categories,
    })


def product_detail(request, slug):
    """
    Detalle de un producto de la tienda
    """
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug, is_active=True
    )
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk).order_by('-is_featured', '-created_at')[:4]
    return render(request, 'core/product_detail.html', {
        'product': product,
        'related_products': related,
    })


def coffee(request):
    """
    Landing page Mega Coffee
    """
    return render(request, 'core/coffee.html')


def services(request):
    """
    Página con todos los servicios
    """
    # Obtener todos los servicios activos agrupados por categoría
    all_services = Service.objects.filter(is_active=True).order_by('name')
    
    # Categorizar servicios
    categories = {
        'Desarrollo Web': [],
        'Hosting y Dominios': [],
        'Marketing Digital': [],
        'Diseño': [],
        'Mantenimiento y Soporte': [],
        'Email y Comunicación': [],
        'Seguridad': [],
        'Optimización': [],
    }
    
    for service in all_services:
        name = service.name
        if any(keyword in name for keyword in ['Landing', 'Sitio', 'Portal', 'commerce', 'Sistema', 'Blog']):
            categories['Desarrollo Web'].append(service)
        elif any(keyword in name for keyword in ['Hosting', 'Servidor', 'Dominio']):
            categories['Hosting y Dominios'].append(service)
        elif any(keyword in name for keyword in ['Redes Sociales', 'Publicidad', 'SEO', 'Marketing', 'Estrategia']):
            categories['Marketing Digital'].append(service)
        elif any(keyword in name for keyword in ['Diseño', 'Logo', 'Identidad', 'Banner', 'Material']):
            categories['Diseño'].append(service)
        elif any(keyword in name for keyword in ['Mantenimiento', 'Soporte']):
            categories['Mantenimiento y Soporte'].append(service)
        elif any(keyword in name for keyword in ['Email', 'Correo', 'Google Workspace']):
            categories['Email y Comunicación'].append(service)
        elif any(keyword in name for keyword in ['SSL', 'Seguridad', 'Backup']):
            categories['Seguridad'].append(service)
        elif any(keyword in name for keyword in ['Optimización', 'Migración', 'Auditoría']):
            categories['Optimización'].append(service)
    
    context = {
        'categories': categories,
        'total_services': all_services.count(),
    }
    return render(request, 'core/services.html', context)


def service_detail(request, slug):
    """
    Página de detalle de un servicio específico
    """
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    from .forms import QuoteRequestForm

    service = get_object_or_404(Service, slug=slug, is_active=True)

    # Handle modal quote form POST (AJAX)
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            from datetime import datetime, timedelta

            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            company = form.cleaned_data.get('company', '')
            srv = form.cleaned_data['service']
            message = form.cleaned_data.get('message', '')

            from apps.clients.models import Client
            client, created = Client.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'phone': phone,
                    'company': company,
                }
            )
            if not created:
                client.name = name
                client.phone = phone
                if company:
                    client.company = company
                client.save()

            quote_number = (
                f"{datetime.now().strftime('%Y%m%d')}"
                f"-{Quote.objects.count() + 1:04d}"
            )
            valid_until = datetime.now().date() + timedelta(days=15)

            admin_user = User.objects.filter(
                role='admin'
            ).first()
            if not admin_user:
                admin_user = User.objects.filter(
                    is_superuser=True
                ).first()

            quote = Quote.objects.create(
                number=quote_number,
                client=client,
                created_by=admin_user,
                status='draft',
                valid_until=valid_until,
                notes=message,
            )

            QuoteItem.objects.create(
                quote=quote,
                service=srv,
                description=srv.description[:500],
                quantity=1,
                unit_price=srv.price,
            )
            quote.calculate_totals()
            quote.status = 'sent'
            quote.save()

            ctx_email = {
                'quote': quote,
                'client': client,
                'service': srv,
                'site_name': 'Megadominio',
            }
            html_msg = render_to_string(
                'emails/quote_request.html', ctx_email
            )
            plain_msg = strip_tags(html_msg)

            try:
                send_mail(
                    subject=(
                        f'Cotización #{quote.number} - {srv.name}'
                    ),
                    message=plain_msg,
                    from_email='info@megadominio.com',
                    recipient_list=[email],
                    html_message=html_msg,
                    fail_silently=False,
                )
            except Exception:
                pass

            return JsonResponse({
                'success': True,
                'message': (
                    '¡Cotización enviada! Revisa tu correo.'
                ),
            })
        else:
            errors = {
                k: v[0] for k, v in form.errors.items()
            }
            return JsonResponse({
                'success': False,
                'errors': errors,
            })

    # GET request
    form = QuoteRequestForm(initial={'service': service})

    # Obtener servicios relacionados (misma categoría aproximada)
    related_services = Service.objects.filter(
        is_active=True,
        billing_type=service.billing_type
    ).exclude(pk=service.pk)[:3]

    context = {
        'service': service,
        'related_services': related_services,
        'form': form,
    }
    return render(request, 'core/service_detail.html', context)


def quote_request(request, service_id=None):
    """
    Página para solicitar cotización
    """
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from .forms import QuoteRequestForm
    from datetime import datetime, timedelta
    
    # Si viene desde un servicio específico, pre-seleccionarlo
    initial_data = {}
    selected_service = None
    if service_id:
        selected_service = get_object_or_404(Service, pk=service_id, is_active=True)
        initial_data['service'] = selected_service
    
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            # Obtener datos del formulario
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            company = form.cleaned_data.get('company', '')
            service = form.cleaned_data['service']
            message = form.cleaned_data.get('message', '')
            
            # Crear o actualizar cliente
            from apps.clients.models import Client
            client, created = Client.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'phone': phone,
                    'company': company,
                }
            )
            
            if not created:
                # Actualizar información si el cliente ya existe
                client.name = name
                client.phone = phone
                if company:
                    client.company = company
                client.save()
            
            # Generar número de cotización
            quote_number = f"{datetime.now().strftime('%Y%m%d')}-{Quote.objects.count() + 1:04d}"
            
            # Crear cotización
            valid_until = datetime.now().date() + timedelta(days=15)
            
            # Obtener el primer usuario admin o crear un usuario sistema
            admin_user = User.objects.filter(is_admin=True).first()
            if not admin_user:
                admin_user = User.objects.filter(is_superuser=True).first()
            
            quote = Quote.objects.create(
                number=quote_number,
                client=client,
                created_by=admin_user if admin_user else request.user,
                status='draft',
                valid_until=valid_until,
                notes=message,
            )
            
            # Crear item de cotización
            QuoteItem.objects.create(
                quote=quote,
                service=service,
                description=service.description,
                quantity=1,
                unit_price=service.price,
            )
            
            # Calcular totales
            quote.calculate_totals()
            
            # Marcar como enviada
            quote.status = 'sent'
            quote.save()
            
            # Preparar email
            context_email = {
                'quote': quote,
                'client': client,
                'service': service,
                'site_name': 'Megadominio',
            }
            
            html_message = render_to_string('emails/quote_request.html', context_email)
            plain_message = strip_tags(html_message)
            
            # Enviar email al cliente
            try:
                send_mail(
                    subject=f'Cotización #{quote.number} - {service.name}',
                    message=plain_message,
                    from_email='info@megadominio.com',
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                messages.success(
                    request,
                    '¡Cotización enviada con éxito! Revisa tu correo electrónico.'
                )
            except Exception as e:
                messages.warning(
                    request,
                    f'Cotización creada pero hubo un error al enviar el email: {str(e)}'
                )
            
            return redirect('core:quote_success', quote_id=quote.id)
    else:
        form = QuoteRequestForm(initial=initial_data)
    
    context = {
        'form': form,
        'selected_service': selected_service,
    }
    return render(request, 'core/quote_request.html', context)


def quote_success(request, quote_id):
    """
    Página de confirmación de cotización enviada
    """
    from django.shortcuts import get_object_or_404
    
    quote = get_object_or_404(Quote, pk=quote_id)
    
    context = {
        'quote': quote,
    }
    return render(request, 'core/quote_success.html', context)
