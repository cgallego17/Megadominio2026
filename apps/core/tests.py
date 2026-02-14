from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from apps.accounts.models import User
from apps.services.models import Service
from apps.quotes.models import Quote


EMAIL_BACKEND_OVERRIDE = {
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
}


class LoginPageTests(TestCase):
    """Tests para la página de login"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass2026!',
            email='test@megadominio.com',
            role='admin',
        )

    def test_login_page_loads(self):
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 200)

    def test_login_page_has_csrf(self):
        resp = self.client.get(self.login_url)
        self.assertContains(resp, 'csrfmiddlewaretoken')

    def test_login_page_has_password_toggle(self):
        resp = self.client.get(self.login_url)
        self.assertContains(resp, 'toggle-password')
        self.assertContains(resp, 'fa-eye')

    def test_login_page_has_forgot_password_link(self):
        resp = self.client.get(self.login_url)
        self.assertContains(resp, 'password_reset')

    def test_login_page_has_honeypot(self):
        resp = self.client.get(self.login_url)
        self.assertContains(resp, 'website_url')

    def test_login_success_redirects(self):
        resp = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass2026!',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard/', resp.url)

    def test_login_wrong_password_stays_on_page(self):
        resp = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(resp.status_code, 200)

    def test_login_empty_fields_stays_on_page(self):
        resp = self.client.post(self.login_url, {
            'username': '',
            'password': '',
        })
        self.assertEqual(resp.status_code, 200)

    def test_login_redirect_authenticated_user(self):
        # Login via POST (axes-compatible)
        self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass2026!',
        })
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 302)


class HoneypotTests(TestCase):
    """Tests para la protección honeypot anti-bot"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='honeypotuser',
            password='TestPass2026!',
            email='honey@megadominio.com',
        )

    def test_honeypot_empty_allows_login(self):
        resp = self.client.post(self.login_url, {
            'username': 'honeypotuser',
            'password': 'TestPass2026!',
            'website_url': '',
        })
        self.assertEqual(resp.status_code, 302)

    def test_honeypot_filled_blocks_request(self):
        resp = self.client.post(self.login_url, {
            'username': 'honeypotuser',
            'password': 'TestPass2026!',
            'website_url': 'http://spam.com',
        })
        self.assertEqual(resp.status_code, 403)

    def test_honeypot_filled_does_not_login(self):
        self.client.post(self.login_url, {
            'username': 'honeypotuser',
            'password': 'TestPass2026!',
            'website_url': 'bot-filled-this',
        })
        # Should not be authenticated — dashboard redirects
        resp = self.client.get(
            reverse('core:dashboard'), follow=False
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)


@override_settings(AXES_FAILURE_LIMIT=3, AXES_COOLOFF_TIME=1)
class BruteForceProtectionTests(TestCase):
    """Tests para protección contra fuerza bruta (django-axes)"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='locktest',
            password='TestPass2026!',
            email='lock@megadominio.com',
        )

    def test_account_locked_after_failures(self):
        for _ in range(3):
            self.client.post(self.login_url, {
                'username': 'locktest',
                'password': 'wrong',
            })
        # Even correct password should be blocked now
        resp = self.client.post(self.login_url, {
            'username': 'locktest',
            'password': 'TestPass2026!',
        })
        self.assertIn(resp.status_code, [403, 429])

    def test_lockout_page_shows_message(self):
        for _ in range(4):
            resp = self.client.post(self.login_url, {
                'username': 'locktest',
                'password': 'wrong',
            })
        # After lockout, response is 403 or 429
        self.assertIn(resp.status_code, [403, 429])


class PasswordResetTests(TestCase):
    """Tests para el flujo de restauración de contraseña"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='resetuser',
            password='TestPass2026!',
            email='reset@megadominio.com',
        )

    def test_password_reset_page_loads(self):
        resp = self.client.get(reverse('password_reset'))
        self.assertEqual(resp.status_code, 200)

    def test_password_reset_form_has_email_field(self):
        resp = self.client.get(reverse('password_reset'))
        self.assertContains(resp, 'id_email')

    def test_password_reset_submit_redirects(self):
        resp = self.client.post(reverse('password_reset'), {
            'email': 'reset@megadominio.com',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('done', resp.url)

    def test_password_reset_done_page(self):
        resp = self.client.get(
            reverse('password_reset_done')
        )
        self.assertEqual(resp.status_code, 200)

    def test_password_reset_complete_page(self):
        resp = self.client.get(
            reverse('password_reset_complete')
        )
        self.assertEqual(resp.status_code, 200)

    def test_password_reset_invalid_email_still_redirects(self):
        resp = self.client.post(reverse('password_reset'), {
            'email': 'noexiste@nada.com',
        })
        self.assertEqual(resp.status_code, 302)


class PublicPagesTests(TestCase):
    """Tests para páginas públicas"""

    def test_home_page(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)

    def test_services_page(self):
        resp = self.client.get(reverse('core:services'))
        self.assertEqual(resp.status_code, 200)

    def test_quote_request_page(self):
        resp = self.client.get(reverse('core:quote_request'))
        self.assertEqual(resp.status_code, 200)

    def test_about_page(self):
        resp = self.client.get(reverse('core:about'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Nosotros')

    def test_contact_page(self):
        resp = self.client.get(reverse('core:contact'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Contacto')

    def test_store_page(self):
        resp = self.client.get(reverse('core:store'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Tienda')

    def test_coffee_page(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Mega')
        self.assertContains(resp, 'COFFEE')

    def test_coffee_has_parallax(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'parallax-layer')
        self.assertContains(resp, 'data-coffee-speed')

    def test_coffee_has_products(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'Deploy Dark')
        self.assertContains(resp, 'Sprint Medium')
        self.assertContains(resp, 'Agile Light')

    def test_coffee_has_jsonld(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'application/ld+json')
        self.assertContains(resp, 'Mega Coffee')

    def test_coffee_has_accessories(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'V60 Dripper')
        self.assertContains(resp, 'Grinder Manual')

    def test_coffee_has_subscriptions(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'Junior Dev')
        self.assertContains(resp, 'Senior Dev')
        self.assertContains(resp, 'Tech Lead')

    def test_store_links_to_coffee(self):
        resp = self.client.get(reverse('core:store'))
        self.assertContains(resp, '/coffee/')

    def test_coffee_has_cart_drawer(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'cart-drawer')
        self.assertContains(resp, 'cart-close')
        self.assertContains(resp, 'cart-items')

    def test_coffee_has_add_to_cart_buttons(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'add-to-cart')
        self.assertContains(resp, 'data-id')
        self.assertContains(resp, 'data-price')

    def test_coffee_has_cart_badge(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'cart-badge-desktop')
        self.assertContains(resp, 'cart-badge-mobile')

    def test_coffee_has_cart_js(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'megacoffee_cart')
        self.assertContains(resp, 'localStorage')

    def test_coffee_cart_checkout_whatsapp(self):
        resp = self.client.get(reverse('core:coffee'))
        self.assertContains(resp, 'wa.me')

    def test_404_page(self):
        resp = self.client.get('/pagina-que-no-existe/')
        self.assertEqual(resp.status_code, 404)


class SEOTests(TestCase):
    """Tests para SEO: sitemap, robots.txt, meta tags, JSON-LD"""

    def test_robots_txt_accessible(self):
        resp = self.client.get('/robots.txt')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/plain')
        self.assertContains(resp, 'Sitemap:')
        self.assertContains(resp, 'Disallow: /admin/')

    def test_sitemap_xml_accessible(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('xml', resp['Content-Type'])

    def test_home_has_meta_description(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, '<meta name="description"')

    def test_home_has_jsonld(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'application/ld+json')
        self.assertContains(resp, 'schema.org')

    def test_home_has_open_graph(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'og:title')
        self.assertContains(resp, 'og:description')

    def test_home_has_canonical(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'rel="canonical"')

    def test_about_has_meta_description(self):
        resp = self.client.get(reverse('core:about'))
        self.assertContains(resp, '<meta name="description"')

    def test_contact_has_jsonld(self):
        resp = self.client.get(reverse('core:contact'))
        self.assertContains(resp, 'LocalBusiness')

    def test_services_has_meta_description(self):
        resp = self.client.get(reverse('core:services'))
        self.assertContains(resp, '<meta name="description"')

    def test_base_has_theme_color(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'theme-color')

    def test_base_has_lang_es(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'lang="es"')

    def test_base_has_preconnect(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'rel="preconnect"')

    def test_font_awesome_deferred(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'rel="preload"')
        self.assertContains(resp, 'font-awesome')

    def test_main_js_deferred(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'main.js" defer')

    def test_gzip_middleware_present(self):
        self.assertIn(
            'django.middleware.gzip.GZipMiddleware',
            settings.MIDDLEWARE,
        )

    def test_nav_has_aria_label(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'aria-label')

    def test_home_has_coffee_float(self):
        resp = self.client.get(reverse('core:home'))
        self.assertContains(resp, 'coffee-intro')
        self.assertContains(resp, 'coffee-parked')
        self.assertContains(resp, 'Es hora de un caf')
        self.assertContains(resp, '/coffee/')


class ServiceDetailTests(TestCase):
    """Tests para la página de detalle de servicio"""

    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(
            name='Test Service',
            description='Descripción de prueba del servicio',
            price=100000,
            billing_type='unique',
            is_active=True,
        )
        self.url = reverse(
            'core:service_detail',
            kwargs={'slug': self.service.slug},
        )

    def test_service_detail_loads(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Test Service')

    def test_service_detail_has_description(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'prueba del servicio')

    def test_service_detail_has_faq_accordion(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'Preguntas frecuentes')
        self.assertContains(resp, 'faq-toggle')

    def test_service_detail_has_quote_modal(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'quote-modal')
        self.assertContains(resp, 'openQuoteModal')

    def test_service_detail_modal_shows_service_name(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'Servicio solicitado')

    def test_service_detail_has_seo_meta(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'og:title')
        self.assertContains(resp, 'twitter:card')
        self.assertContains(resp, 'canonical')

    def test_service_detail_has_jsonld(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'application/ld+json')
        self.assertContains(resp, 'FAQPage')

    def test_service_detail_hides_prices(self):
        resp = self.client.get(self.url)
        self.assertNotContains(resp, '$100')
        self.assertContains(resp, 'Solicita tu cotización')

    def test_service_detail_inactive_returns_404(self):
        self.service.is_active = False
        self.service.save()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 404)


@override_settings(**EMAIL_BACKEND_OVERRIDE)
class QuoteModalAjaxTests(TestCase):
    """Tests para el envío AJAX del modal de cotización"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='quoteadmin',
            password='AdminPass2026!',
            email='quoteadmin@megadominio.com',
            role='admin',
        )
        self.service = Service.objects.create(
            name='Web Dev',
            description='Desarrollo web profesional',
            price=500000,
            billing_type='unique',
            is_active=True,
        )
        self.url = reverse(
            'core:service_detail',
            kwargs={'slug': self.service.slug},
        )

    def _post_quote(self, **overrides):
        data = {
            'name': 'Juan Pérez',
            'email': 'juan@test.com',
            'phone': '+57 300 123 4567',
            'company': 'Mi Empresa',
            'service': self.service.pk,
            'message': 'Necesito un sitio web',
        }
        data.update(overrides)
        return self.client.post(
            self.url, data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

    def test_valid_post_returns_success(self):
        resp = self._post_quote()
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['success'])

    def test_valid_post_creates_quote(self):
        self._post_quote(email='new@test.com')
        self.assertEqual(Quote.objects.count(), 1)
        quote = Quote.objects.first()
        self.assertEqual(quote.status, 'sent')

    def test_valid_post_creates_client(self):
        from apps.clients.models import Client as CM
        self._post_quote(email='pedro@test.com')
        self.assertTrue(
            CM.objects.filter(email='pedro@test.com').exists()
        )

    def test_missing_fields_returns_errors(self):
        resp = self._post_quote(
            name='', email='', phone=''
        )
        data = resp.json()
        self.assertFalse(data['success'])
        self.assertIn('name', data['errors'])
        self.assertIn('email', data['errors'])
        self.assertIn('phone', data['errors'])

    def test_invalid_email_returns_error(self):
        resp = self._post_quote(email='not-an-email')
        data = resp.json()
        self.assertFalse(data['success'])
        self.assertIn('email', data['errors'])


class DashboardAccessTests(TestCase):
    """Tests para control de acceso al dashboard"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.admin = User.objects.create_user(
            username='dashadmin',
            password='AdminPass2026!',
            role='admin',
        )
        self.regular = User.objects.create_user(
            username='dashclient',
            password='RegularPass2026!',
            role='client',
        )

    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse('core:dashboard'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)

    def test_dashboard_admin_access(self):
        # Login via POST (axes-compatible)
        self.client.post(self.login_url, {
            'username': 'dashadmin',
            'password': 'AdminPass2026!',
        })
        resp = self.client.get(reverse('core:dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_client_redirected(self):
        self.client.post(self.login_url, {
            'username': 'dashclient',
            'password': 'RegularPass2026!',
        })
        resp = self.client.get(reverse('core:dashboard'))
        self.assertEqual(resp.status_code, 302)


class SecuritySettingsTests(TestCase):
    """Tests para verificar configuraciones de seguridad"""

    def test_csrf_use_sessions(self):
        self.assertTrue(settings.CSRF_USE_SESSIONS)

    def test_csrf_cookie_httponly(self):
        self.assertTrue(settings.CSRF_COOKIE_HTTPONLY)

    def test_session_cookie_httponly(self):
        self.assertTrue(settings.SESSION_COOKIE_HTTPONLY)

    def test_x_frame_options_deny(self):
        self.assertEqual(settings.X_FRAME_OPTIONS, 'DENY')

    def test_content_type_nosniff(self):
        self.assertTrue(settings.SECURE_CONTENT_TYPE_NOSNIFF)

    def test_browser_xss_filter(self):
        self.assertTrue(settings.SECURE_BROWSER_XSS_FILTER)

    def test_referrer_policy(self):
        self.assertEqual(
            settings.SECURE_REFERRER_POLICY,
            'strict-origin-when-cross-origin',
        )

    def test_password_min_length_10(self):
        validators = settings.AUTH_PASSWORD_VALIDATORS
        min_len_validator = next(
            (v for v in validators
             if 'MinimumLength' in v['NAME']),
            None,
        )
        self.assertIsNotNone(min_len_validator)
        self.assertEqual(
            min_len_validator['OPTIONS']['min_length'], 10
        )

    def test_argon2_is_default_hasher(self):
        self.assertIn(
            'Argon2', settings.PASSWORD_HASHERS[0]
        )

    def test_axes_failure_limit(self):
        self.assertEqual(settings.AXES_FAILURE_LIMIT, 5)

    def test_axes_cooloff_time(self):
        self.assertEqual(settings.AXES_COOLOFF_TIME, 1)

    def test_axes_reset_on_success(self):
        self.assertTrue(settings.AXES_RESET_ON_SUCCESS)

    def test_axes_in_installed_apps(self):
        self.assertIn('axes', settings.INSTALLED_APPS)

    def test_axes_middleware_present(self):
        self.assertIn(
            'axes.middleware.AxesMiddleware',
            settings.MIDDLEWARE,
        )

    def test_axes_backend_present(self):
        self.assertIn(
            'axes.backends.AxesStandaloneBackend',
            settings.AUTHENTICATION_BACKENDS,
        )


class SecurityHeadersTests(TestCase):
    """Tests para verificar headers de seguridad en respuestas"""

    def test_x_frame_options_header(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(
            resp.get('X-Frame-Options'), 'DENY'
        )

    def test_x_content_type_options_header(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(
            resp.get('X-Content-Type-Options'), 'nosniff'
        )

    def test_referrer_policy_header(self):
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(
            resp.get('Referrer-Policy'),
            'strict-origin-when-cross-origin',
        )


class ServiceDescriptionsTests(TestCase):
    """Tests para verificar que los servicios tienen descripciones"""

    def test_top_services_have_long_descriptions(self):
        top_names = [
            'Desarrollo Web',
            'Marketing Digital',
            'SEO / Posicionamiento',
        ]
        for name in top_names:
            svc = Service.objects.filter(name=name).first()
            if svc:
                self.assertGreater(
                    len(svc.description), 3000,
                    f'{name}: {len(svc.description)} chars',
                )

    def test_all_services_have_descriptions(self):
        for svc in Service.objects.all():
            self.assertGreater(
                len(svc.description), 100,
                f'{svc.name} has no real description',
            )

    def test_services_exist(self):
        count = Service.objects.filter(
            is_active=True
        ).count()
        self.assertGreaterEqual(count, 6)
