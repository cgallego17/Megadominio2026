from django.db import models
from django.contrib.auth.models import User


class Service(models.Model):
    """Modelo para gestionar los servicios ofrecidos"""
    
    BILLING_TYPE_CHOICES = [
        ('unique', 'Pago único'),
        ('monthly', 'Mensual'),
        ('annual', 'Anual'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre del servicio")
    description = models.TextField(verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    billing_type = models.CharField(
        max_length=10, 
        choices=BILLING_TYPE_CHOICES, 
        default='unique',
        verbose_name="Tipo de facturación"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ClientService(models.Model):
    """Modelo para asignar servicios a clientes"""
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('cancelled', 'Cancelado'),
    ]
    
    client = models.ForeignKey(
        'clients.Client', 
        on_delete=models.CASCADE, 
        verbose_name="Cliente"
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        verbose_name="Servicio"
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name="Estado"
    )
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Fecha de fin"
    )
    monthly_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio mensual"
    )
    notes = models.TextField(
        blank=True, 
        verbose_name="Notas"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Servicio del cliente"
        verbose_name_plural = "Servicios de clientes"
        ordering = ['-created_at']
        unique_together = ['client', 'service']
    
    def __str__(self):
        return f"{self.client.name} - {self.service.name}"
