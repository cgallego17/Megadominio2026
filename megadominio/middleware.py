"""
Middleware para rechazar peticiones con Host inválido sin llenar los logs.
Evita tracebacks por bots que envían Host: 0.0.0.0 u otros no permitidos.
"""
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.http.request import validate_host


class ValidateHostHeaderMiddleware:
    """
    Si el Host no está permitido (ALLOWED_HOSTS), responde 400 inmediatamente
    sin que Django levante DisallowedHost (y sin traceback en logs).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get("HTTP_HOST", "").split(":")[0].strip().lower()
        if host and not validate_host(settings.ALLOWED_HOSTS, host):
            return HttpResponseBadRequest("Bad Request")
        return self.get_response(request)
