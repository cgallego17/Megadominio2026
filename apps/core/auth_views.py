import logging
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden

logger = logging.getLogger('security')


class SecureLoginView(LoginView):
    """
    Login view with honeypot anti-bot protection and
    security logging.
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        # Honeypot check: if bot filled the hidden field, reject
        honeypot = request.POST.get('website_url', '')
        if honeypot:
            logger.warning(
                'Honeypot triggered from IP %s',
                self._get_client_ip(request),
            )
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1>'
            )
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        logger.warning(
            'Failed login attempt for user "%s" from IP %s',
            self.request.POST.get('username', ''),
            self._get_client_ip(self.request),
        )
        return super().form_invalid(form)

    def _get_client_ip(self, request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
