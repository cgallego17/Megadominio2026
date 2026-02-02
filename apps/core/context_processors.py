from django.conf import settings


def site_context(request):
    """
    Context processor para agregar variables globales del sitio
    """
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'Megadominio'),
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
    }
