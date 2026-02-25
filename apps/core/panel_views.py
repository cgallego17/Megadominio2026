from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from io import BytesIO
import zipfile
from django.db.models import Sum
from apps.clients.models import Client
from apps.services.models import ClientService, ClientEmailAccount
from apps.store.models import Order
from apps.invoices.models import CuentaDeCobro
from apps.accounts.models import UserAddress, State, City
from .forms import (
    ProfileForm, PasswordChangeForm, UserAddressForm,
    ClientEmailAccountForm, ClientEmailPasswordChangeForm,
)
from apps.services.cpanel_api import CpanelAPI, CpanelAPIError
from apps.services.cpanel_config import get_cpanel_config


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
def panel_servicio_emails(request, pk):
    """Administración de cuentas de correo para un servicio del cliente."""
    client = get_client_for_user(request.user)
    if not client:
        return HttpResponseForbidden("No tienes acceso a este servicio.")

    client_service = get_object_or_404(
        ClientService.objects.select_related('service', 'client'),
        pk=pk,
        client=client,
    )
    if not client_service.is_email_service:
        messages.warning(
            request,
            'Este servicio no corresponde a correo electrónico.',
        )
        return redirect('core:panel_servicios')

    accounts = client_service.email_accounts.all().order_by('email')
    limit = client_service.email_accounts_limit
    can_add_more = (limit == 0) or (accounts.count() < limit)

    if request.method == 'POST':
        if not can_add_more:
            messages.error(
                request,
                'Ya alcanzaste el límite de cuentas habilitadas para este servicio.',
            )
            return redirect('core:panel_servicio_emails', pk=pk)

        form = ClientEmailAccountForm(request.POST)
        if form.is_valid():
            email_account = form.save(commit=False)
            email_account.client_service = client_service
            email_account.save()
            messages.success(request, 'Cuenta de correo creada correctamente.')
            return redirect('core:panel_servicio_emails', pk=pk)
    else:
        form = ClientEmailAccountForm()

    return render(request, 'panel/panel_servicio_emails.html', {
        'client_service': client_service,
        'accounts': accounts,
        'limit': limit,
        'can_add_more': can_add_more,
        'form': form,
    })


@login_required
def panel_servicio_email_delete(request, pk, email_pk):
    """Eliminar una cuenta de correo de un servicio del cliente."""
    client = get_client_for_user(request.user)
    if not client:
        return HttpResponseForbidden("No tienes acceso a este servicio.")

    client_service = get_object_or_404(ClientService, pk=pk, client=client)
    email_account = get_object_or_404(
        ClientEmailAccount,
        pk=email_pk,
        client_service=client_service,
    )

    if request.method == 'POST':
        email_account.delete()
        messages.success(request, 'Cuenta de correo eliminada.')

    return redirect('core:panel_servicio_emails', pk=pk)


@login_required
def panel_servicio_email_password(request, pk, email_pk):
    """Cambiar contraseña de una cuenta de correo desde el panel del cliente."""
    client = get_client_for_user(request.user)
    if not client:
        return HttpResponseForbidden("No tienes acceso a este servicio.")

    client_service = get_object_or_404(ClientService, pk=pk, client=client)
    email_account = get_object_or_404(
        ClientEmailAccount,
        pk=email_pk,
        client_service=client_service,
    )

    if request.method == 'POST':
        form = ClientEmailPasswordChangeForm(request.POST)
        if form.is_valid():
            cfg = get_cpanel_config()
            if not cfg.sync_enabled:
                messages.error(
                    request,
                    "La sincronización con cPanel está desactivada. Contacta soporte.",
                )
                return redirect('core:panel_servicio_emails', pk=pk)

            if not cfg.cpanel_ready:
                messages.error(
                    request,
                    "No se puede actualizar: faltan Host, Usuario o API Token de cPanel.",
                )
                return redirect('core:panel_servicio_emails', pk=pk)

            cpanel = CpanelAPI(
                host=cfg.host,
                username=cfg.username,
                api_token=cfg.api_token,
                use_https=cfg.use_https,
                port=cfg.port,
                timeout=cfg.timeout,
            )
            try:
                cpanel.update_mailbox_password(
                    email=email_account.email,
                    new_password=form.cleaned_data['new_password'],
                )
                messages.success(
                    request,
                    f'Contraseña actualizada para {email_account.email}.',
                )
                return redirect('core:panel_servicio_emails', pk=pk)
            except CpanelAPIError as exc:
                messages.error(
                    request,
                    f'No se pudo actualizar la contraseña en cPanel: {exc}',
                )
    else:
        form = ClientEmailPasswordChangeForm()

    return render(request, 'panel/panel_servicio_email_password.html', {
        'client_service': client_service,
        'email_account': email_account,
        'form': form,
    })


@login_required
def panel_servicio_email_outlook_prf(request, pk, email_pk):
    """Descarga un archivo .prf para autoconfigurar Outlook clásico."""
    client = get_client_for_user(request.user)
    if not client:
        return HttpResponseForbidden("No tienes acceso a este servicio.")

    client_service = get_object_or_404(ClientService, pk=pk, client=client)
    email_account = get_object_or_404(
        ClientEmailAccount,
        pk=email_pk,
        client_service=client_service,
    )

    account_name = email_account.email
    display_name = email_account.display_name or client.name or account_name
    local_part, domain = account_name.split('@', 1)

    cfg = get_cpanel_config()
    email_host = getattr(settings, 'EMAIL_HOST', '') or ''
    imap_host = cfg.outlook_imap_host or email_host
    smtp_host = cfg.outlook_smtp_host or email_host
    imap_port = cfg.outlook_imap_port
    smtp_port = cfg.outlook_smtp_port
    imap_ssl = cfg.outlook_imap_ssl
    smtp_ssl = cfg.outlook_smtp_ssl

    # Nota: por seguridad no se incluye contraseña en el archivo.
    prf_content = f"""[General]
Custom=1
ProfileName=Megadominio-{local_part}
DefaultProfile=Yes
OverwriteProfile=Yes
ModifyDefaultProfileIfPresent=True

[Service List]
Service1=Microsoft Outlook Client
Service2=Outlook Address Book
Service3=Internet E-mail

[Service3]
AccountName={account_name}
DisplayName={display_name}
EmailAddress={account_name}
ReplyAddress={account_name}
ReplyE-Mail={account_name}
MailAccountType=IMAP
IncomingServer={imap_host}
IncomingUserName={account_name}
IncomingPort={imap_port}
IncomingUseSSL={1 if imap_ssl else 0}
OutgoingServer={smtp_host}
OutgoingUserName={account_name}
OutgoingPort={smtp_port}
OutgoingUseSSL={1 if smtp_ssl else 0}
SMTPUseAuth=1
SPA=0
Domain={domain}
LeaveOnServer=1
"""

    filename = f"outlook-autoconfig-{local_part}.prf"
    response = HttpResponse(prf_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def panel_servicio_email_outlook_pack(request, pk, email_pk):
    """Descarga ZIP con .prf + .bat para importación 1 clic en Outlook clásico."""
    client = get_client_for_user(request.user)
    if not client:
        return HttpResponseForbidden("No tienes acceso a este servicio.")

    client_service = get_object_or_404(ClientService, pk=pk, client=client)
    email_account = get_object_or_404(
        ClientEmailAccount,
        pk=email_pk,
        client_service=client_service,
    )

    account_name = email_account.email
    local_part, _domain = account_name.split('@', 1)
    display_name = email_account.display_name or client.name or account_name

    cfg = get_cpanel_config()
    email_host = getattr(settings, 'EMAIL_HOST', '') or ''
    imap_host = cfg.outlook_imap_host or email_host
    smtp_host = cfg.outlook_smtp_host or email_host
    imap_port = cfg.outlook_imap_port
    smtp_port = cfg.outlook_smtp_port
    imap_ssl = cfg.outlook_imap_ssl
    smtp_ssl = cfg.outlook_smtp_ssl

    prf_filename = f"outlook-autoconfig-{local_part}.prf"
    bat_filename = "instalar-outlook.bat"
    readme_filename = "LEEME.txt"

    prf_content = f"""[General]
Custom=1
ProfileName=Megadominio-{local_part}
DefaultProfile=Yes
OverwriteProfile=Yes
ModifyDefaultProfileIfPresent=True

[Service List]
Service1=Microsoft Outlook Client
Service2=Outlook Address Book
Service3=Internet E-mail

[Service3]
AccountName={account_name}
DisplayName={display_name}
EmailAddress={account_name}
ReplyAddress={account_name}
ReplyE-Mail={account_name}
MailAccountType=IMAP
IncomingServer={imap_host}
IncomingUserName={account_name}
IncomingPort={imap_port}
IncomingUseSSL={1 if imap_ssl else 0}
OutgoingServer={smtp_host}
OutgoingUserName={account_name}
OutgoingPort={smtp_port}
OutgoingUseSSL={1 if smtp_ssl else 0}
SMTPUseAuth=1
SPA=0
LeaveOnServer=1
"""

    bat_content = f"""@echo off
setlocal
set PRF=%~dp0{prf_filename}
set OUTLOOK_EXE=

if not exist "%PRF%" (
  echo No se encontro el archivo PRF: %PRF%
  pause
  exit /b 1
)

rem Buscar Outlook en rutas comunes (365/2021/2019/2016, x64/x86)
for %%P in (
  "%ProgramFiles%\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"
  "%ProgramFiles(x86)%\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE"
  "%ProgramFiles%\\Microsoft Office\\Office16\\OUTLOOK.EXE"
  "%ProgramFiles(x86)%\\Microsoft Office\\Office16\\OUTLOOK.EXE"
  "%ProgramFiles%\\Microsoft Office\\Office15\\OUTLOOK.EXE"
  "%ProgramFiles(x86)%\\Microsoft Office\\Office15\\OUTLOOK.EXE"
  "%ProgramFiles%\\Microsoft Office\\Office14\\OUTLOOK.EXE"
  "%ProgramFiles(x86)%\\Microsoft Office\\Office14\\OUTLOOK.EXE"
) do (
  if exist %%~P (
    set OUTLOOK_EXE=%%~P
    goto :found
  )
)

echo No se encontro OUTLOOK.EXE en rutas comunes.
echo Abre Outlook clasico manualmente e importa el archivo:
echo %PRF%
pause
exit /b 1

:found
echo Importando perfil con:
echo %OUTLOOK_EXE%
"%OUTLOOK_EXE%" /importprf "%PRF%"

echo.
echo Si Outlook no abre, inicia Outlook clasico manualmente.
echo Luego ingresa la contrasena del correo cuando te la solicite.
pause
"""

    readme_content = (
        "Pasos:\r\n"
        "1) Descomprime este ZIP en una carpeta.\r\n"
        "2) Ejecuta instalar-outlook.bat como usuario normal.\r\n"
        "3) Abre Outlook clasico (no el nuevo Outlook).\r\n"
        f"4) Usuario de correo: {account_name}\r\n"
        "5) Ingresa la contrasena cuando Outlook la solicite.\r\n"
    )

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(prf_filename, prf_content)
        zf.writestr(bat_filename, bat_content)
        zf.writestr(readme_filename, readme_content)

    zip_buffer.seek(0)
    zip_name = f"outlook-1clic-{local_part}.zip"
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_name}"'
    return response


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
    from apps.core.dashboard_views import dashboard_cuenta_pdf
    return dashboard_cuenta_pdf.__wrapped__.__wrapped__(request, pk)


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
