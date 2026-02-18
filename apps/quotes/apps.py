from django.apps import AppConfig


class QuotesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.quotes'
    verbose_name = 'Cotizaciones'

    def ready(self):
        # Importar señales para notificaciones de cambios en cotizaciones
        from . import signals  # noqa: F401
