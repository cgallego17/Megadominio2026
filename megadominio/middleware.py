"""
Middleware de seguridad para Megadominio.

Capa 1 — ValidateHostHeaderMiddleware:
    Rechaza peticiones con Host inválido (bots, scanners, rutas de socket).
    Evita DisallowedHost tracebacks en logs.

Capa 2 — BlockScannerPathsMiddleware:
    Bloquea rutas de bots (wp-admin, .env, *.php…)
    Responde 404 silencioso.

Capa 3 — LoginRateLimitMiddleware:
    Limita intentos de login por IP: 10 fallos en 5 min → 429.
    Trabaja junto a django-axes (que bloquea por cuenta).

Capa 4 — PasswordResetRateLimitMiddleware:
    Limita solicitudes de recuperación de contraseña por IP:
    5 en 15 min → 429.
"""
from __future__ import annotations

import logging
import re

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import DisallowedHost, SuspiciousOperation
from django.http import HttpResponse
from django.http.request import validate_host

security_logger = logging.getLogger("security")

# Host estilo RFC para HTTP (dominio o IPv6 entre corchetes), opcional :puerto
_HOST_HEADER_RE = re.compile(
    r"^("
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*\.?"
    r"|localhost"
    r"|\d{1,3}(?:\.\d{1,3}){3}"
    r"|\[[a-f0-9:]+\]"
    r")"
    r"(?::\d+)?"
    r"$",
    re.IGNORECASE,
)

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
    "/admin/config.php",
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
    ".php",
    ".asp",
    ".aspx",
    ".jsp",
    ".cgi",
    ".bak",
    ".sql",
    ".tar",
    ".gz",
    ".zip",
    ".rar",
)

# ── Configuración de rate limiting ─────────────────────────────────────────

LOGIN_RATE_LIMIT = 10  # intentos máximos
LOGIN_RATE_WINDOW = 300  # ventana en segundos (5 min)

RESET_RATE_LIMIT = 5  # solicitudes máximas de reset
RESET_RATE_WINDOW = 900  # ventana en segundos (15 min)


def _get_client_ip(request):
    """Obtiene la IP real del cliente respetando X-Forwarded-For."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _host_domain(raw_host: str) -> str:
    """Extrae el dominio del header Host (soporta IPv6 [addr]:port)."""
    host = (raw_host or "").strip().lower()
    if host.startswith("["):
        end = host.find("]")
        if end != -1:
            return host[: end + 1]
    # Dominio o IPv4: quitar :puerto (solo el último segmento numérico)
    if host.count(":") == 1:
        name, maybe_port = host.rsplit(":", 1)
        if maybe_port.isdigit():
            return name
    return host.rstrip(":")


# ── Middleware classes ──────────────────────────────────────────────────────


class ValidateHostHeaderMiddleware:
    """
    Si el Host no es un dominio RFC válido o no está en ALLOWED_HOSTS,
    responde 400 silencioso (sin DisallowedHost / traceback).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        raw = (request.META.get("HTTP_HOST") or "").strip()
        # Bots / proxies mal formados: Host vacío, rutas Unix (/var/www/....sock), etc.
        if (
            not raw
            or "/" in raw
            or "\\" in raw
            or " " in raw
            or not _HOST_HEADER_RE.match(raw)
        ):
            return HttpResponse(status=400)

        domain = _host_domain(raw)
        allowed = settings.ALLOWED_HOSTS or []
        try:
            # Firma correcta: validate_host(host, allowed_hosts)
            if not validate_host(domain, allowed):
                return HttpResponse(status=400)
        except (DisallowedHost, SuspiciousOperation, TypeError, ValueError):
            return HttpResponse(status=400)

        try:
            return self.get_response(request)
        except DisallowedHost:
            # Red de seguridad si algún código llama request.get_host() después
            return HttpResponse(status=400)


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
        if request.method == "POST" and request.path_info == "/accounts/login/":
            ip = _get_client_ip(request)
            cache_key = f"login_attempts_ip_{ip}"
            attempts = cache.get(cache_key, 0)

            if attempts >= LOGIN_RATE_LIMIT:
                security_logger.warning(
                    "LOGIN_RATE_LIMIT_EXCEEDED ip=%s attempts=%d",
                    ip,
                    attempts,
                )
                return HttpResponse(
                    "<h1>429 — Demasiados intentos.</h1>"
                    "<p>Espera 5 minutos antes de intentarlo de nuevo.</p>",
                    status=429,
                    content_type="text/html",
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
            request.method == "POST"
            and request.path_info == "/accounts/password_reset/"
        ):
            ip = _get_client_ip(request)
            cache_key = f"pwreset_attempts_ip_{ip}"
            attempts = cache.get(cache_key, 0)

            if attempts >= RESET_RATE_LIMIT:
                security_logger.warning(
                    "PWRESET_RATE_LIMIT_EXCEEDED ip=%s attempts=%d",
                    ip,
                    attempts,
                )
                return HttpResponse(
                    "<h1>429 — Demasiados intentos.</h1>"
                    "<p>Espera 15 minutos antes de intentarlo de nuevo.</p>",
                    status=429,
                    content_type="text/html",
                )

            cache.set(cache_key, attempts + 1, RESET_RATE_WINDOW)

        return self.get_response(request)
