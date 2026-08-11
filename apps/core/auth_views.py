import time
import logging
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponseForbidden

security_logger = logging.getLogger('security')

# Debe coincidir con LOGIN_RATE_LIMIT en middleware.py
_LOGIN_CACHE_PREFIX = 'login_attempts_ip_'


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


class SecureLoginView(LoginView):
    """
    Login view con protección multicapa:
    - Honeypot anti-bot (campo oculto website_url)
    - Penalización de 1 segundo en fallos (ralentiza fuerza bruta)
    - Logging enriquecido (IP + User-Agent) para detectar bots
    - Limpia el contador de rate limiting al hacer login exitoso
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        # ── Honeypot: bots que llenan campos ocultos son rechazados ──
        if request.POST.get('website_url', ''):
            ip = _get_client_ip(request)
            security_logger.warning(
                'HONEYPOT_TRIGGERED action=login ip=%s ua="%s"',
                ip,
                request.META.get('HTTP_USER_AGENT', '')[:200],
            )
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Login exitoso — limpiar contador de rate limit para esta IP."""
        ip = _get_client_ip(self.request)
        cache.delete(f'{_LOGIN_CACHE_PREFIX}{ip}')
        security_logger.info(
            'LOGIN_SUCCESS user="%s" ip=%s',
            form.get_user().email,
            ip,
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Login fallido — registrar y aplicar penalización."""
        ip = _get_client_ip(self.request)
        username = self.request.POST.get('username', '')
        ua = self.request.META.get('HTTP_USER_AGENT', '')[:200]
        security_logger.warning(
            'LOGIN_FAILED user="%s" ip=%s ua="%s"',
            username, ip, ua,
        )
        # Penalización: ralentiza ataques de fuerza bruta
        time.sleep(1)
        return super().form_invalid(form)

