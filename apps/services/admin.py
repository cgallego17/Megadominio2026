from django import forms
from django.conf import settings
from django.contrib import admin, messages
from .models import Service, ClientService, ClientEmailAccount
from .cpanel_api import CpanelAPI, CpanelAPIError


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
            sync_enabled = getattr(settings, "CPANEL_SYNC_ENABLED", False)
            if is_new and sync_enabled and not cleaned_data.get("cpanel_password"):
                self.add_error(
                    "cpanel_password",
                    "Este campo es obligatorio cuando la sincronización cPanel está activa.",
                )
            return cleaned_data

    form = CpanelSyncForm

    class Media:
        js = ("admin/js/cpanel_password_generator.js",)

    def _cpanel_client(self):
        return CpanelAPI(
            host=getattr(settings, "CPANEL_HOST", ""),
            username=getattr(settings, "CPANEL_USERNAME", ""),
            api_token=getattr(settings, "CPANEL_API_TOKEN", ""),
            use_https=getattr(settings, "CPANEL_USE_HTTPS", True),
            port=getattr(settings, "CPANEL_PORT", 2083),
            timeout=getattr(settings, "CPANEL_TIMEOUT", 20),
        )

    def _cpanel_ready(self):
        required = (
            getattr(settings, "CPANEL_HOST", ""),
            getattr(settings, "CPANEL_USERNAME", ""),
            getattr(settings, "CPANEL_API_TOKEN", ""),
        )
        return all(required)

    def save_model(self, request, obj, form, change):
        previous = None
        if change:
            previous = ClientEmailAccount.objects.filter(pk=obj.pk).first()

        super().save_model(request, obj, form, change)

        if not getattr(settings, "CPANEL_SYNC_ENABLED", False):
            return

        if not self._cpanel_ready():
            self.message_user(
                request,
                "Sincronización cPanel activa, pero faltan variables CPANEL_HOST/CPANEL_USERNAME/CPANEL_API_TOKEN.",
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
                    quota_mb=getattr(settings, "CPANEL_MAILBOX_QUOTA_MB", 2048),
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
        should_sync = getattr(settings, "CPANEL_SYNC_ENABLED", False)
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
