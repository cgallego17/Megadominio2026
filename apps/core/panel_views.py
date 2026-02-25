from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Sum
from apps.clients.models import Client
from apps.services.models import ClientService
from apps.store.models import Order
from apps.invoices.models import CuentaDeCobro
from apps.accounts.models import UserAddress, State, City
from .forms import ProfileForm, PasswordChangeForm, UserAddressForm


def get_client_for_user(user):
    """Obtiene el Client vinculado al usuario, o None."""
    try:
        return user.client_profile
    except Client.DoesNotExist:
        return None


@login_required
def panel_home(request):
    """Panel principal del usuario — resumen."""
    client = get_client_for_user(request.user)

    # Servicios contratados
    services = []
    active_services_count = 0
    recent_cuentas = []
    total_cuentas = 0
    if client:
        services = ClientService.objects.filter(
            client=client
        ).select_related('service').order_by('-created_at')[:5]
        active_services_count = ClientService.objects.filter(
            client=client, status='active'
        ).count()
        cuentas_qs = CuentaDeCobro.objects.filter(client=client).order_by('-created_at')
        total_cuentas = cuentas_qs.count()
        recent_cuentas = cuentas_qs[:5]

    # Órdenes de la tienda (por email o por created_by)
    orders = Order.objects.filter(
        customer_email=request.user.email
    ) | Order.objects.filter(
        created_by=request.user
    )
    orders = orders.distinct().order_by('-created_at')
    total_orders = orders.count()
    recent_orders = orders[:5]
    total_spent = orders.filter(
        payment_status='approved'
    ).aggregate(t=Sum('total'))['t'] or 0

    return render(request, 'panel/panel_home.html', {
        'client': client,
        'services': services,
        'active_services_count': active_services_count,
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'recent_cuentas': recent_cuentas,
        'total_cuentas': total_cuentas,
    })


@login_required
def panel_servicios(request):
    """Listado de servicios contratados del usuario."""
    client = get_client_for_user(request.user)

    services = []
    if client:
        services = ClientService.objects.filter(
            client=client
        ).select_related('service').order_by('-created_at')

    return render(request, 'panel/panel_servicios.html', {
        'client': client,
        'services': services,
    })


@login_required
def panel_compras(request):
    """Listado de compras/órdenes del usuario."""
    orders = Order.objects.filter(
        customer_email=request.user.email
    ) | Order.objects.filter(
        created_by=request.user
    )
    orders = orders.distinct().order_by('-created_at')

    return render(request, 'panel/panel_compras.html', {
        'orders': orders,
    })


@login_required
def panel_compra_detail(request, pk):
    """Detalle de una compra del usuario."""
    order = get_object_or_404(Order, pk=pk)
    # Verificar que la orden pertenece al usuario
    is_owner = (
        order.customer_email == request.user.email
        or order.created_by == request.user
    )
    if not is_owner:
        return HttpResponseForbidden("No tienes acceso a esta orden.")

    return render(request, 'panel/panel_compra_detail.html', {
        'order': order,
    })


@login_required
def panel_cuentas(request):
    """Listado de cuentas de cobro emitidas al cliente."""
    client = get_client_for_user(request.user)
    cuentas = []
    if client:
        cuentas = CuentaDeCobro.objects.filter(
            client=client
        ).order_by('-created_at')

    return render(request, 'panel/panel_cuentas.html', {
        'client': client,
        'cuentas': cuentas,
    })


@login_required
def panel_cuenta_pdf(request, pk):
    """Descargar PDF de una cuenta de cobro propia."""
    client = get_client_for_user(request.user)
    if not client:
        return HttpResponseForbidden("No tienes acceso a esta cuenta de cobro.")

    cuenta = get_object_or_404(CuentaDeCobro, pk=pk)
    if cuenta.client_id != client.id:
        return HttpResponseForbidden("No tienes acceso a esta cuenta de cobro.")

    # Reutiliza la misma generación PDF del dashboard.
    from . import dashboard_views as dv
    return dv.dashboard_cuenta_pdf.__wrapped__.__wrapped__(request, pk)


@login_required
def panel_perfil(request):
    """Editar información del perfil del usuario."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('core:panel_perfil')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'panel/panel_perfil.html', {
        'form': form,
    })


@login_required
def panel_password(request):
    """Cambiar contraseña del usuario."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('core:panel_perfil')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'panel/panel_password.html', {
        'form': form,
    })


@login_required
def panel_direcciones(request):
    """Listado de direcciones del usuario + formulario para agregar."""
    addresses = request.user.addresses.all()

    if request.method == 'POST':
        form = UserAddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, 'Dirección agregada correctamente.')
            return redirect('core:panel_direcciones')
    else:
        form = UserAddressForm()

    return render(request, 'panel/panel_direcciones.html', {
        'addresses': addresses,
        'form': form,
    })


@login_required
def panel_direccion_edit(request, pk):
    """Editar una dirección existente."""
    addr = get_object_or_404(UserAddress, pk=pk, user=request.user)

    if request.method == 'POST':
        form = UserAddressForm(request.POST, instance=addr)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada.')
            return redirect('core:panel_direcciones')
    else:
        form = UserAddressForm(instance=addr)

    return render(request, 'panel/panel_direccion_edit.html', {
        'form': form,
        'address': addr,
    })


@login_required
def panel_direccion_delete(request, pk):
    """Eliminar una dirección."""
    addr = get_object_or_404(UserAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        addr.delete()
        messages.success(request, 'Dirección eliminada.')
    return redirect('core:panel_direcciones')


@login_required
def panel_direccion_default(request, pk):
    """Marcar una dirección como principal."""
    addr = get_object_or_404(UserAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        addr.is_default = True
        addr.save()
        messages.success(
            request,
            f'"{addr.label}" marcada como dirección principal.'
        )
    return redirect('core:panel_direcciones')


# ── API endpoints for cascading geo selects ──

def api_states(request):
    """Return states for a given country_id."""
    country_id = request.GET.get('country_id')
    if not country_id:
        return JsonResponse([], safe=False)
    qs = State.objects.filter(
        country_id=country_id
    ).order_by('name').values('id', 'name')
    return JsonResponse(list(qs), safe=False)


def api_cities(request):
    """Return cities for a given state_id."""
    state_id = request.GET.get('state_id')
    if not state_id:
        return JsonResponse([], safe=False)
    qs = City.objects.filter(
        state_id=state_id
    ).order_by('name').values('id', 'name')
    return JsonResponse(list(qs), safe=False)
