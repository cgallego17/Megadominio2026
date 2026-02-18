from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.store'
    verbose_name = 'Tienda'

    def ready(self):
        # Importar señales para activar envíos de correo en cambios de orden
        from . import signals  # noqa: F401
