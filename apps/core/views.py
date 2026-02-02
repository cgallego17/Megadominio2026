from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from apps.quotes.models import Quote
from apps.invoices.models import Invoice
from apps.clients.models import Client
from apps.services.models import Service, ClientService
from apps.accounts.models import User


def home(request):
    """
    Vista principal del sitio - Home comercial
    """
    context = {
        'services': Service.objects.filter(is_active=True)[:6],
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    """
    Dashboard administrativo con métricas principales
    """
    if not request.user.is_admin and not request.user.is_advisor:
        return redirect('home')
    
    # Métricas generales
    total_quotes = Quote.objects.count()
    total_clients = Client.objects.count()
    total_services = Service.objects.filter(is_active=True).count()
    total_invoices = Invoice.objects.count()
    
    # Cotizaciones por estado
    quotes_by_status = Quote.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Facturas por estado
    invoices_by_status = Invoice.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
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
