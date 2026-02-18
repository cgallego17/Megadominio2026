import logging
import time

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.urls import reverse

from .forms import SignupForm
from apps.core.emails import send_admin_notification

logger = logging.getLogger('security')

SIGNUP_RATE_LIMIT = 5          # max attempts
SIGNUP_RATE_WINDOW = 600       # per 10 minutes


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def signup(request):
    """Vista de registro público de usuarios."""
    if request.user.is_authenticated:
        return redirect('core:panel_home')

    client_ip = _get_client_ip(request)

    if request.method == 'POST':
        # ---- Rate limiting by IP ----
        cache_key = f'signup_attempts_{client_ip}'
        attempts = cache.get(cache_key, 0)
        if attempts >= SIGNUP_RATE_LIMIT:
            logger.warning(
                'Signup rate limit exceeded from IP %s', client_ip
            )
            return HttpResponseForbidden(
                '<h1>Demasiados intentos de registro. '
                'Intenta de nuevo en 10 minutos.</h1>'
            )

        # ---- Honeypot check ----
        if request.POST.get('website_url', ''):
            logger.warning(
                'Signup honeypot triggered from IP %s', client_ip
            )
            time.sleep(2)
            return HttpResponseForbidden('<h1>403 Forbidden</h1>')

        form = SignupForm(request.POST)
        cache.set(cache_key, attempts + 1, SIGNUP_RATE_WINDOW)

        if form.is_valid():
            user = form.save()
            logger.info(
                'New user registered: %s from IP %s',
                user.email, client_ip
            )
            cache.delete(cache_key)
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')

            # Notificar al administrador del sistema
            try:
                admin_url = request.build_absolute_uri(
                    reverse('core:dashboard_user_detail', args=[user.id])
                )
                send_admin_notification(
                    title='Nuevo registro de usuario',
                    body=f"Usuario: {user.get_full_name() or user.email} <{user.email}>\nIP: {client_ip}",
                    cta_url=admin_url,
                    cta_label='Ver usuario',
                )
            except Exception:
                pass
            next_url = request.GET.get('next', '')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('core:panel_home')
        else:
            logger.info(
                'Failed signup attempt from IP %s', client_ip
            )
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})
