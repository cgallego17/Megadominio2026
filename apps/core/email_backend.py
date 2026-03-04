"""
Backend de correo que lee la configuración SMTP desde la base de datos (EmailConfig).
Si no hay configuración o está vacía, usa las variables EMAIL_* de settings.
"""
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend


class DatabaseEmailBackend(SMTPBackend):
    """
    Backend SMTP que usa EmailConfig de la BD si está configurado.
    """
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, use_ssl=None, fail_silently=False, **kwargs):
        config = self._get_config()
        if config:
            host = host or config.smtp_host
            port = port or config.smtp_port
            username = username or config.smtp_user
            password = password or config.decrypted_password
            use_tls = config.smtp_use_tls if use_tls is None else use_tls
            use_ssl = config.smtp_use_ssl if use_ssl is None else use_ssl

        if not host:
            host = getattr(settings, 'EMAIL_HOST', '')
        if port is None:
            port = getattr(settings, 'EMAIL_PORT', 465)
        if username is None:
            username = getattr(settings, 'EMAIL_HOST_USER', '')
        if password is None:
            password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        if use_tls is None:
            use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
        if use_ssl is None:
            use_ssl = getattr(settings, 'EMAIL_USE_SSL', True)

        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            fail_silently=fail_silently,
            **kwargs,
        )

    def _get_config(self):
        """Obtiene EmailConfig si existe y tiene host configurado."""
        try:
            from django.apps import apps
            if not apps.is_installed('apps.services'):
                return None
            from apps.services.models import EmailConfig
            cfg = EmailConfig.objects.first()
            if cfg and cfg.smtp_host:
                return cfg
        except Exception:
            pass
        return None
