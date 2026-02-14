from django.db import models
from django.conf import settings
from django.utils.text import slugify


class ProductCategory(models.Model):
    """Categoría de productos de la tienda"""
    name = models.CharField('Nombre', max_length=100)
    slug = models.SlugField('Slug', max_length=120, unique=True, blank=True)
    icon = models.CharField(
        'Icono FontAwesome', max_length=50, default='fa-tag',
        help_text='Clase FA, ej: fa-tshirt, fa-coffee, fa-sticky-note'
    )
    order = models.PositiveIntegerField('Orden', default=0)
    is_active = models.BooleanField('Activa', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría de producto'
        verbose_name_plural = 'Categorías de productos'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Producto de la tienda"""
    BADGE_CHOICES = [
        ('', 'Sin badge'),
        ('new', 'NUEVO'),
        ('popular', 'POPULAR'),
        ('sale', 'OFERTA'),
        ('limited', 'LIMITADO'),
    ]

    name = models.CharField('Nombre', max_length=200)
    slug = models.SlugField('Slug', max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='products',
        verbose_name='Categoría'
    )
    description = models.TextField('Descripción', blank=True)
    image = models.ImageField(
        'Imagen', upload_to='products/', blank=True, null=True,
        help_text='Imagen del producto (recomendado 600x600px)'
    )
    price = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(
        'Precio anterior', max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text='Precio tachado (opcional, para mostrar descuento)'
    )
    icon = models.CharField(
        'Icono FontAwesome', max_length=50, default='fa-box',
        help_text='Clase FA, ej: fa-tshirt, fa-mug-hot, fa-mouse'
    )
    icon_color = models.CharField(
        'Color del icono', max_length=30, default='text-red-500',
        help_text='Clase Tailwind, ej: text-red-500, text-amber-400'
    )
    badge = models.CharField(
        'Badge', max_length=20, choices=BADGE_CHOICES,
        blank=True, default=''
    )
    stock = models.PositiveIntegerField('Stock', default=0)
    is_active = models.BooleanField('Activo', default=True)
    is_featured = models.BooleanField('Destacado', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def badge_color(self):
        colors = {
            'new': 'bg-red-600',
            'popular': 'bg-orange-500',
            'sale': 'bg-green-500',
            'limited': 'bg-purple-500',
        }
        return colors.get(self.badge, '')

    @property
    def badge_label(self):
        labels = {
            'new': 'NUEVO',
            'popular': 'POPULAR',
            'sale': 'OFERTA',
            'limited': 'LIMITADO',
        }
        return labels.get(self.badge, '')


class Order(models.Model):
    """Orden de compra de la tienda"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('processing', 'En proceso'),
        ('shipped', 'Enviada'),
        ('delivered', 'Entregada'),
        ('cancelled', 'Cancelada'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('declined', 'Rechazado'),
        ('voided', 'Anulado'),
        ('error', 'Error'),
    ]

    number = models.CharField('Número', max_length=20, unique=True)
    customer_name = models.CharField('Nombre del cliente', max_length=200)
    customer_email = models.EmailField('Email', blank=True)
    customer_phone = models.CharField('Teléfono', max_length=30, blank=True)
    customer_address = models.TextField('Dirección de envío', blank=True)
    customer_country = models.CharField(
        'País', max_length=100, blank=True
    )
    customer_state = models.CharField(
        'Departamento', max_length=100, blank=True
    )
    customer_city = models.CharField(
        'Ciudad', max_length=100, blank=True
    )
    customer_document = models.CharField(
        'Documento de identidad', max_length=30, blank=True
    )
    status = models.CharField(
        'Estado', max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    subtotal = models.DecimalField(
        'Subtotal', max_digits=12, decimal_places=2, default=0
    )
    shipping_cost = models.DecimalField(
        'Costo de envío', max_digits=10, decimal_places=2, default=0
    )
    discount = models.DecimalField(
        'Descuento', max_digits=10, decimal_places=2, default=0
    )
    total = models.DecimalField(
        'Total', max_digits=12, decimal_places=2, default=0
    )
    notes = models.TextField('Notas', blank=True)
    # Wompi payment fields
    wompi_transaction_id = models.CharField(
        'Wompi Transaction ID', max_length=100, blank=True, db_index=True
    )
    payment_status = models.CharField(
        'Estado de pago', max_length=20,
        choices=PAYMENT_STATUS_CHOICES, default='pending'
    )
    payment_method = models.CharField(
        'Método de pago', max_length=50, blank=True
    )
    paid_at = models.DateTimeField('Fecha de pago', null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='store_orders',
        verbose_name='Creada por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.number} - {self.customer_name}'

    def calculate_totals(self):
        items_total = sum(
            item.subtotal for item in self.items.all()
        )
        self.subtotal = items_total
        self.total = items_total + self.shipping_cost - self.discount
        self.save(update_fields=['subtotal', 'total'])


class OrderItem(models.Model):
    """Item de una orden"""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items',
        verbose_name='Orden'
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='order_items',
        verbose_name='Producto'
    )
    description = models.CharField('Descripción', max_length=300)
    quantity = models.PositiveIntegerField('Cantidad', default=1)
    unit_price = models.DecimalField(
        'Precio unitario', max_digits=10, decimal_places=2
    )
    subtotal = models.DecimalField(
        'Subtotal', max_digits=12, decimal_places=2, default=0
    )

    class Meta:
        verbose_name = 'Item de orden'
        verbose_name_plural = 'Items de orden'

    def __str__(self):
        return f'{self.description} x{self.quantity}'

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
