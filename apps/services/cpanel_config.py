"""Helper para leer configuración de cPanel desde el admin (CpanelConfig) o desde settings."""

from django.conf import settings

from .models import CpanelConfig


def get_cpanel_config():
    """
    Devuelve la configuración de cPanel. Si existe un CpanelConfig en la BD, se usa;
    si no, se lee de settings (variables de entorno).
    """
    try:
        cfg = CpanelConfig.objects.first()
    except Exception:
        cfg = None

    if cfg is not None:
        return _Config(
            sync_enabled=cfg.sync_enabled,
            host=cfg.host or "",
            username=cfg.username or "",
            api_token=cfg.api_token or "",
            use_https=cfg.use_https,
            port=cfg.port,
            timeout=cfg.timeout,
            mailbox_quota_mb=cfg.mailbox_quota_mb,
            outlook_imap_host=cfg.outlook_imap_host or "",
            outlook_imap_port=cfg.outlook_imap_port,
            outlook_imap_ssl=cfg.outlook_imap_ssl,
            outlook_smtp_host=cfg.outlook_smtp_host or "",
            outlook_smtp_port=cfg.outlook_smtp_port,
            outlook_smtp_ssl=cfg.outlook_smtp_ssl,
        )

    return _Config(
        sync_enabled=getattr(settings, "CPANEL_SYNC_ENABLED", False),
        host=getattr(settings, "CPANEL_HOST", ""),
        username=getattr(settings, "CPANEL_USERNAME", ""),
        api_token=getattr(settings, "CPANEL_API_TOKEN", ""),
        use_https=getattr(settings, "CPANEL_USE_HTTPS", True),
        port=getattr(settings, "CPANEL_PORT", 2083),
        timeout=getattr(settings, "CPANEL_TIMEOUT", 20),
        mailbox_quota_mb=getattr(settings, "CPANEL_MAILBOX_QUOTA_MB", 2048),
        outlook_imap_host=getattr(settings, "OUTLOOK_IMAP_HOST", "") or getattr(settings, "EMAIL_HOST", ""),
        outlook_imap_port=int(getattr(settings, "OUTLOOK_IMAP_PORT", 993)),
        outlook_imap_ssl=bool(getattr(settings, "OUTLOOK_IMAP_SSL", True)),
        outlook_smtp_host=getattr(settings, "OUTLOOK_SMTP_HOST", "") or getattr(settings, "EMAIL_HOST", ""),
        outlook_smtp_port=int(getattr(settings, "OUTLOOK_SMTP_PORT", 465)),
        outlook_smtp_ssl=bool(getattr(settings, "OUTLOOK_SMTP_SSL", True)),
    )


class _Config:
    def __init__(
        self,
        sync_enabled=False,
        host="",
        username="",
        api_token="",
        use_https=True,
        port=2083,
        timeout=20,
        mailbox_quota_mb=2048,
        outlook_imap_host="",
        outlook_imap_port=993,
        outlook_imap_ssl=True,
        outlook_smtp_host="",
        outlook_smtp_port=465,
        outlook_smtp_ssl=True,
    ):
        self.sync_enabled = sync_enabled
        self.host = host
        self.username = username
        self.api_token = api_token
        self.use_https = use_https
        self.port = port
        self.timeout = timeout
        self.mailbox_quota_mb = mailbox_quota_mb
        self.outlook_imap_host = outlook_imap_host
        self.outlook_imap_port = outlook_imap_port
        self.outlook_imap_ssl = outlook_imap_ssl
        self.outlook_smtp_host = outlook_smtp_host
        self.outlook_smtp_port = outlook_smtp_port
        self.outlook_smtp_ssl = outlook_smtp_ssl

    @property
    def cpanel_ready(self):
        return bool(self.host and self.username and self.api_token)
