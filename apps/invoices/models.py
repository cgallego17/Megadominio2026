from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

User = get_user_model()


class Invoice(models.Model):
    """Modelo para gestionar facturas/cuentas de cobro"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagada'),
        ('overdue', 'Vencida'),
        ('cancelled', 'Cancelada'),
    ]
    
    number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de factura"
    )
    quote = models.OneToOneField(
        'quotes.Quote',
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name="Cotización"
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='invoices',
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
        default='pending',
        verbose_name="Estado"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Subtotal"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Descuento"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Impuesto"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total"
    )
    issue_date = models.DateField(
        verbose_name="Fecha de emisión"
    )
    due_date = models.DateField(
        verbose_name="Fecha de vencimiento"
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de pago"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas"
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
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"INV-{self.number}"
    
    def mark_as_paid(self):
        """Marca la factura como pagada"""
        self.status = 'paid'
        self.paid_date = datetime.date.today()
        self.save()
    
    @property
    def is_overdue(self):
        """Verifica si la factura está vencida"""
        if self.status != 'pending':
            return False
        return datetime.date.today() > self.due_date


class InvoiceItem(models.Model):
    """Modelo para los items de una factura"""
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Factura"
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
    
    class Meta:
        verbose_name = "Item de factura"
        verbose_name_plural = "Items de factura"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.invoice.number} - {self.service.name}"


@receiver(post_save, sender=Invoice)
def create_invoice_items(sender, instance, created, **kwargs):
    """Crea automáticamente los items de la factura basados en la cotización"""
    if created:
        for quote_item in instance.quote.items.all():
            InvoiceItem.objects.create(
                invoice=instance,
                service=quote_item.service,
                description=quote_item.description,
                quantity=quote_item.quantity,
                unit_price=quote_item.unit_price,
                subtotal=quote_item.subtotal
            )
