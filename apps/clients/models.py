from django.db import models
from django.conf import settings


class Client(models.Model):
    """Modelo para gestionar clientes"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('dni', 'DNI'),
        ('passport', 'Pasaporte'),
        ('rtn', 'RTN'),
        ('other', 'Otro'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_profile',
        verbose_name="Usuario vinculado"
    )
    name = models.CharField(max_length=200, verbose_name="Nombre completo")
    email = models.EmailField(verbose_name="Correo electrónico")
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Teléfono"
    )
    document_type = models.CharField(
        max_length=10,
        choices=DOCUMENT_TYPE_CHOICES,
        default='dni',
        verbose_name="Tipo de documento"
    )
    document_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Número de documento"
    )
    address = models.TextField(
        blank=True,
        verbose_name="Dirección"
    )
    company = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Empresa"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_quotes(self):
        """Retorna el número total de cotizaciones"""
        return self.quotes.count()
    
    @property
    def active_services(self):
        """Retorna el número de servicios activos"""
        return self.clientservices.filter(status='active').count()
    
    @property
    def pending_invoices(self):
        """Retorna el número de facturas pendientes"""
        return self.invoices.filter(status='pending').count()
    
    @property
    def pending_cuentas_de_cobro(self):
        """Retorna el número de cuentas de cobro pendientes"""
        return self.cuentas_de_cobro.filter(status='pending').count()