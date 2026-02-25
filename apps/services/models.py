from django.db import models
from django.utils.text import slugify


class Service(models.Model):
    """Modelo para gestionar los servicios ofrecidos"""
    
    BILLING_TYPE_CHOICES = [
        ('unique', 'Pago único'),
        ('monthly', 'Mensual'),
        ('annual', 'Anual'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre del servicio")
    slug = models.SlugField(
        max_length=250, unique=True, blank=True,
        verbose_name="Slug"
    )
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Service.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse(
            'core:service_detail', kwargs={'slug': self.slug}
        )


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
    # Tipo de precio para este cliente/servicio (único, mensual o anual)
    billing_type = models.CharField(
        max_length=10,
        choices=Service.BILLING_TYPE_CHOICES,
        default='monthly',
        verbose_name="Tipo de precio",
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
        verbose_name="Valor"
    )
    renewal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor renovación",
        help_text="Si es 0, se asumirá el mismo valor del campo 'Valor'",
    )
    email_accounts_limit = models.PositiveIntegerField(
        default=0,
        verbose_name="Cuentas de correo habilitadas",
        help_text="Aplica para servicios de correo/email. 0 = sin habilitar.",
    )
    notes = models.TextField(
        blank=True, 
        verbose_name="Notas"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    reminder_15_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Recordatorio 15 días enviado",
    )
    reminder_3_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Recordatorio 3 días enviado",
    )
    expired_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Notificación de vencido enviada",
    )
    auto_disabled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deshabilitado automático",
    )
    
    class Meta:
        verbose_name = "Servicio del cliente"
        verbose_name_plural = "Servicios de clientes"
        ordering = ['-created_at']
        unique_together = ['client', 'service']
    
    def __str__(self):
        return f"{self.client.name} - {self.service.name}"

    @property
    def is_email_service(self):
        """Determina si este servicio es de tipo correo/email."""
        text = (
            f"{self.service.name} {self.service.description}".lower()
        )
        keywords = (
            "email", "correo", "mail", "workspace",
            "google workspace", "smtp", "imap", "pop3",
            "buzon", "buzón", "cuenta de correo",
        )
        return any(word in text for word in keywords)


class ClientEmailAccount(models.Model):
    """Cuentas de correo administradas por el cliente para un servicio email."""

    client_service = models.ForeignKey(
        ClientService,
        on_delete=models.CASCADE,
        related_name="email_accounts",
        verbose_name="Servicio del cliente",
    )
    email = models.EmailField(
        max_length=255,
        verbose_name="Correo",
    )
    display_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nombre para mostrar",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización",
    )

    class Meta:
        verbose_name = "Cuenta de correo del cliente"
        verbose_name_plural = "Cuentas de correo de clientes"
        ordering = ["email"]
        unique_together = ["client_service", "email"]

    def __str__(self):
        return f"{self.client_service.client.name} - {self.email}"
