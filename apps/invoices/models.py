from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import datetime

User = get_user_model()


class Invoice(models.Model):
    """Modelo para gestionar facturas fiscales (documento tributario formal)"""
    
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


class CuentaDeCobro(models.Model):
    """
    Modelo para gestionar cuentas de cobro.
    Documento de cobro independiente - puede crearse con o sin cotización previa.
    Diferente de Invoice (factura fiscal) que es el documento tributario formal.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagada'),
        ('overdue', 'Vencida'),
        ('cancelled', 'Cancelada'),
    ]
    
    number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de cuenta de cobro"
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='cuentas_de_cobro',
        verbose_name="Cliente"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        verbose_name="Creado por"
    )
    quote = models.ForeignKey(
        'quotes.Quote',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuentas_de_cobro',
        verbose_name="Cotización (opcional)"
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
        default=0,
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
        default=0,
        verbose_name="Impuesto"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Total"
    )
    tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15,
        verbose_name="Impuesto (%)"
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
        verbose_name = "Cuenta de cobro"
        verbose_name_plural = "Cuentas de cobro"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"CC-{self.number}"
    
    def mark_as_paid(self):
        """Marca la cuenta de cobro como pagada"""
        self.status = 'paid'
        self.paid_date = datetime.date.today()
        self.save()
    
    def calculate_totals(self):
        """Calcula los totales a partir de los items"""
        subtotal = sum(item.subtotal for item in self.items.all())
        self.subtotal = subtotal
        base_imponible = subtotal - self.discount_amount
        self.tax_amount = base_imponible * (self.tax_percentage / 100)
        self.total = base_imponible + self.tax_amount
        self.save()
    
    @property
    def is_overdue(self):
        """Verifica si la cuenta de cobro está vencida"""
        if self.status != 'pending':
            return False
        return datetime.date.today() > self.due_date


class CuentaDeCobroItem(models.Model):
    """Modelo para los items de una cuenta de cobro"""
    
    cuenta_de_cobro = models.ForeignKey(
        CuentaDeCobro,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Cuenta de cobro"
    )
    service = models.ForeignKey(
        'services.Service',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Servicio (opcional)"
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
    
    class Meta:
        verbose_name = "Item de cuenta de cobro"
        verbose_name_plural = "Items de cuenta de cobro"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.cuenta_de_cobro.number} - {self.description[:30]}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)


@receiver(post_save, sender=CuentaDeCobroItem)
@receiver(post_delete, sender=CuentaDeCobroItem)
def update_cuenta_de_cobro_totals(sender, instance, **kwargs):
    """Actualiza los totales de la cuenta de cobro cuando se modifican los items"""
    instance.cuenta_de_cobro.calculate_totals()


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
