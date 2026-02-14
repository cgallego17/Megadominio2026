from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardTestCase(TestCase):
    """Verifica que el dashboard cargue correctamente"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='dashboard_test',
            email='test@test.com',
            password='testpass123',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        self.client = Client()

    def test_dashboard_loads_for_admin(self):
        """El dashboard debe cargar para usuarios admin"""
        self.client.login(username='dashboard_test', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.content)
        self.assertNotIn(b'Traceback', response.content)
        self.assertIn(b'Cuentas de cobro', response.content)
