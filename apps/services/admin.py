from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import reverse

from .models import Service, ClientService, ClientEmailAccount, CpanelConfig
from .cpanel_api import CpanelAPI, CpanelAPIError
from .cpanel_config import get_cpanel_config


@admin.register(CpanelConfig)
class CpanelConfigAdmin(admin.ModelAdmin):
    """Configuración de cPanel y correo (Outlook .prf). Una sola entrada."""
    list_display = (
        "sync_enabled",
        "host",
        "username",
        "outlook_imap_host",
        "outlook_smtp_host",
        "updated_at",
    )
    fieldsets = (
        ("Conexión cPanel", {
            "fields": (
                "sync_enabled",
                "host",
                "username",
                "api_token",
                "use_https",
                "port",
                "timeout",
                "mailbox_quota_mb",
            ),
            "description": "Usado al crear/editar/eliminar cuentas de correo en Admin.",
        }),
        ("Outlook (.prf)", {
            "fields": (
                "outlook_imap_host",
                "outlook_imap_port",
                "outlook_imap_ssl",
                "outlook_smtp_host",
                "outlook_smtp_port",
                "outlook_smtp_ssl",
            ),
            "description": "Servidores para el archivo de autoconfiguración Outlook que descarga el cliente.",
        }),
    )

    def has_add_permission(self, request):
        return not CpanelConfig.objects.exists()

    def changelist_view(self, request, extra_context=None):
        obj = CpanelConfig.objects.first()
        if obj is not None:
            return redirect(reverse("admin:services_cpanelconfig_change", args=(obj.pk,)))
        return super().changelist_view(request, extra_context)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'billing_type', 'is_active')
    list_filter = ('billing_type', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Información de facturación', {
            'fields': ('price', 'billing_type')
        }),
    )


@admin.register(ClientService)
class ClientServiceAdmin(admin.ModelAdmin):
    list_display = (
        'client', 'service', 'status', 'start_date',
        'monthly_price', 'email_accounts_limit',
    )
    list_filter = ('status', 'start_date')
    search_fields = ('client__name', 'service__name')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Asignación', {
            'fields': ('client', 'service')
        }),
        ('Estado y fechas', {
            'fields': ('status', 'start_date', 'end_date')
        }),
        ('Información financiera', {
            'fields': ('monthly_price', 'renewal_price', 'email_accounts_limit')
        }),
        ('Información adicional', {
            'fields': ('notes',)
        }),
    )


@admin.register(ClientEmailAccount)
class ClientEmailAccountAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'display_name', 'client_service',
        'is_active', 'created_at',
    )
    list_filter = ('is_active', 'created_at')
    search_fields = (
        'email', 'display_name',
        'client_service__client__name',
        'client_service__service__name',
    )

    class CpanelSyncForm(forms.ModelForm):
        cpanel_password = forms.CharField(
            required=False,
            widget=forms.PasswordInput(
                render_value=False,
                attrs={"autocomplete": "new-password"},
            ),
            label="Password cPanel",
            help_text=(
                "Solo para crear el buzón en cPanel. "
                "No se guarda en base de datos."
            ),
        )
        cpanel_new_password = forms.CharField(
            required=False,
            widget=forms.PasswordInput(
                render_value=False,
                attrs={"autocomplete": "new-password"},
            ),
            label="Nueva password cPanel",
            help_text=(
                "Opcional al editar. Si la escribes, se cambia la contraseña "
                "del buzón en cPanel."
            ),
        )

        class Meta:
            model = ClientEmailAccount
            fields = "__all__"

        def clean(self):
            cleaned_data = super().clean()
            is_new = self.instance.pk is None
            cfg = get_cpanel_config()
            if is_new and cfg.sync_enabled and not cleaned_data.get("cpanel_password"):
                self.add_error(
                    "cpanel_password",
                    "Este campo es obligatorio cuando la sincronización cPanel está activa.",
                )
            return cleaned_data

    form = CpanelSyncForm

    class Media:
        js = ("admin/js/cpanel_password_generator.js",)

    def _cpanel_client(self):
        cfg = get_cpanel_config()
        return CpanelAPI(
            host=cfg.host,
            username=cfg.username,
            api_token=cfg.api_token,
            use_https=cfg.use_https,
            port=cfg.port,
            timeout=cfg.timeout,
        )

    def _cpanel_ready(self):
        return get_cpanel_config().cpanel_ready

    def save_model(self, request, obj, form, change):
        previous = None
        if change:
            previous = ClientEmailAccount.objects.filter(pk=obj.pk).first()

        super().save_model(request, obj, form, change)

        cfg = get_cpanel_config()
        if not cfg.sync_enabled:
            return

        if not self._cpanel_ready():
            self.message_user(
                request,
                "Sincronización cPanel activa, pero faltan Host, Usuario o API Token. "
                "Configúralos en Servicios > Configuración cPanel / correo.",
                level=messages.WARNING,
            )
            return

        client = self._cpanel_client()

        try:
            if not change:
                raw_password = form.cleaned_data.get("cpanel_password")
                client.create_mailbox(
                    email=obj.email,
                    password=raw_password,
                    quota_mb=cfg.mailbox_quota_mb,
                )
                self.message_user(
                    request,
                    f"Cuenta {obj.email} creada en cPanel.",
                    level=messages.SUCCESS,
                )
                return

            if previous and previous.email != obj.email:
                self.message_user(
                    request,
                    "El correo fue cambiado en Django. Renombrado en cPanel no es automático; crea/elimina manualmente o ajusta con script.",
                    level=messages.WARNING,
                )

            if previous and previous.is_active != obj.is_active:
                if obj.is_active:
                    client.unsuspend_mailbox(obj.email)
                    msg = f"Cuenta {obj.email} activada en cPanel."
                else:
                    client.suspend_mailbox(obj.email)
                    msg = f"Cuenta {obj.email} suspendida en cPanel."
                self.message_user(request, msg, level=messages.SUCCESS)

            new_password = form.cleaned_data.get("cpanel_new_password")
            if change and new_password:
                client.update_mailbox_password(
                    email=obj.email,
                    new_password=new_password,
                )
                self.message_user(
                    request,
                    f"Password de {obj.email} actualizada en cPanel.",
                    level=messages.SUCCESS,
                )
        except CpanelAPIError as exc:
            self.message_user(
                request,
                f"Error de sincronización con cPanel: {exc}",
                level=messages.ERROR,
            )

    def delete_model(self, request, obj):
        email = obj.email
        cfg = get_cpanel_config()
        should_sync = cfg.sync_enabled
        ready = self._cpanel_ready()

        super().delete_model(request, obj)

        if not should_sync:
            return
        if not ready:
            self.message_user(
                request,
                "No se eliminó en cPanel porque faltan variables de conexión.",
                level=messages.WARNING,
            )
            return

        client = self._cpanel_client()
        try:
            client.delete_mailbox(email)
            self.message_user(
                request,
                f"Cuenta {email} eliminada en cPanel.",
                level=messages.SUCCESS,
            )
        except CpanelAPIError as exc:
            self.message_user(
                request,
                f"La cuenta se eliminó en Django, pero falló en cPanel: {exc}",
                level=messages.ERROR,
            )
