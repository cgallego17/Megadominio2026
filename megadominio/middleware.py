"""
Middleware de seguridad para Megadominio.

Capa 1 — ValidateHostHeaderMiddleware:
    Rechaza peticiones con Host inválido (bots, scanners).
    Evita DisallowedHost tracebacks en logs.

Capa 2 — BlockScannerPathsMiddleware:
    Bloquea rutas de bots (wp-admin, .env, wrangler.toml…)
    Responde 404 silencioso.

Capa 3 — LoginRateLimitMiddleware:
    Limita intentos de login por IP: 10 fallos en 5 min → 429.
    Trabaja junto a django-axes (que bloquea por cuenta).

Capa 4 — PasswordResetRateLimitMiddleware:
    Limita solicitudes de recuperación de contraseña por IP:
    5 en 15 min → 429.
"""
import logging
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.http.request import validate_host

security_logger = logging.getLogger('security')

# ── Rutas bloqueadas ────────────────────────────────────────────────────────

BLOCKED_PATH_PREFIXES = (
    "/wrangler.toml",
    "/.env",
    "/.git",
    "/wp-admin",
    "/wp-login",
    "/wp-content",
    "/wp-includes",
    "/xmlrpc.php",
    "/phpmyadmin",
    "/pma",
    "/.well-known/traffic-advice",
    "/config.json",
    "/configuration.php",
    "/administrator",
    "/shell",
    "/cmd",
    "/cgi-bin",
    "/boaform",
    "/HNAP1",
    "/vendor/phpunit",
    "/telescope",
    "/horizon",
    "/.DS_Store",
    "/setup.php",
    "/install.php",
)

BLOCKED_EXTENSIONS = (
    ".php", ".asp", ".aspx", ".jsp", ".cgi",
    ".bak", ".sql", ".tar", ".gz", ".zip", ".rar",
)

# ── Configuración de rate limiting ─────────────────────────────────────────

LOGIN_RATE_LIMIT = 10       # intentos máximos
LOGIN_RATE_WINDOW = 300     # ventana en segundos (5 min)

RESET_RATE_LIMIT = 5        # solicitudes máximas de reset
RESET_RATE_WINDOW = 900     # ventana en segundos (15 min)


def _get_client_ip(request):
    """Obtiene la IP real del cliente respetando X-Forwarded-For."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


# ── Middleware classes ──────────────────────────────────────────────────────

class ValidateHostHeaderMiddleware:
    """
    Si el Host no está en ALLOWED_HOSTS, devuelve una respuesta
    vacía y silenciosa — sin traceback, sin info útil para el bot.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get(
            "HTTP_HOST", ""
        ).split(":")[0].strip().lower()
        if host and not validate_host(settings.ALLOWED_HOSTS, host):
            return HttpResponse(status=400)
        return self.get_response(request)


class BlockScannerPathsMiddleware:
    """
    Bloquea rutas y extensiones típicas de bots/scanners antes de
    que lleguen al router de Django. Retorna 404 silencioso.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.lower()
        if path.startswith(BLOCKED_PATH_PREFIXES):
            return HttpResponse(status=404)
        if path.endswith(BLOCKED_EXTENSIONS):
            return HttpResponse(status=404)
        return self.get_response(request)


class LoginRateLimitMiddleware:
    """
    Rate limiting por IP en el endpoint de login.

    - Intercepta solo POST a /accounts/login/
    - Cuenta intentos usando Django cache
    - Tras LOGIN_RATE_LIMIT intentos en LOGIN_RATE_WINDOW segundos
      devuelve HTTP 429 y registra la IP en el log de seguridad
    - El contador se resetea cuando el login es exitoso
      (eso lo maneja SecureLoginView en auth_views.py)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == 'POST'
            and request.path_info == '/accounts/login/'
        ):
            ip = _get_client_ip(request)
            cache_key = f'login_attempts_ip_{ip}'
            attempts = cache.get(cache_key, 0)

            if attempts >= LOGIN_RATE_LIMIT:
                security_logger.warning(
                    'LOGIN_RATE_LIMIT_EXCEEDED ip=%s attempts=%d',
                    ip, attempts,
                )
                return HttpResponse(
                    '<h1>429 — Demasiados intentos.</h1>'
                    '<p>Espera 5 minutos antes de intentarlo de nuevo.</p>',
                    status=429,
                    content_type='text/html',
                )

            # Incrementar contador; TTL se renueva con cada intento
            cache.set(cache_key, attempts + 1, LOGIN_RATE_WINDOW)

        return self.get_response(request)


class PasswordResetRateLimitMiddleware:
    """
    Rate limiting por IP en el endpoint de recuperación de contraseña.

    - Intercepta POST a /accounts/password_reset/
    - Tras RESET_RATE_LIMIT intentos en RESET_RATE_WINDOW segundos
      devuelve HTTP 429
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == 'POST'
            and request.path_info == '/accounts/password_reset/'
        ):
            ip = _get_client_ip(request)
            cache_key = f'pwreset_attempts_ip_{ip}'
            attempts = cache.get(cache_key, 0)

            if attempts >= RESET_RATE_LIMIT:
                security_logger.warning(
                    'PWRESET_RATE_LIMIT_EXCEEDED ip=%s attempts=%d',
                    ip, attempts,
                )
                return HttpResponse(
                    '<h1>429 — Demasiados intentos.</h1>'
                    '<p>Espera 15 minutos antes de intentarlo de nuevo.</p>',
                    status=429,
                    content_type='text/html',
                )

            cache.set(cache_key, attempts + 1, RESET_RATE_WINDOW)

        return self.get_response(request)


