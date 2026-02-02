from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Quote(models.Model):
    """Modelo para gestionar cotizaciones"""
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
        ('expired', 'Expirada'),
    ]
    
    number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de cotización"
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='quotes',
        verbose_name="Cliente"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        verbose_name="Creado por"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Estado"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Subtotal"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Descuento (%)"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Descuento"
    )
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15,
        verbose_name="Impuesto (%)"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Impuesto"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Total"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas"
    )
    valid_until = models.DateField(
        verbose_name="Válida hasta"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    class Meta:
        verbose_name = "Cotización"
        verbose_name_plural = "Cotizaciones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"COT-{self.number}"
    
    def calculate_totals(self):
        """Calcula los totales de la cotización"""
        subtotal = sum(item.subtotal for item in self.items.all())
        
        discount_amount = (subtotal * self.discount_percentage) / 100
        subtotal_after_discount = subtotal - discount_amount
        
        tax_amount = (subtotal_after_discount * self.tax_percentage) / 100
        total = subtotal_after_discount + tax_amount
        
        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.tax_amount = tax_amount
        self.total = total
        self.save()


class QuoteItem(models.Model):
    """Modelo para los items de una cotización"""
    
    quote = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Cotización"
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        verbose_name="Servicio"
    )
    description = models.CharField(
        max_length=500,
        verbose_name="Descripción"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio unitario"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Subtotal"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    class Meta:
        verbose_name = "Item de cotización"
        verbose_name_plural = "Items de cotización"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quote.number} - {self.service.name}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.quote.calculate_totals()
