from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Modelo de usuario extendido"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('advisor', 'Asesor'),
        ('seller', 'Vendedor'),
        ('client', 'Cliente'),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Rol"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Avatar"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificado"
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
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        permissions = [
            ('can_view_dashboard', 'Puede ver el dashboard'),
            ('can_manage_quotes', 'Puede gestionar cotizaciones'),
            ('can_manage_invoices', 'Puede gestionar facturas'),
            ('can_manage_clients', 'Puede gestionar clientes'),
            ('can_manage_services', 'Puede gestionar servicios'),
        ]
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_advisor(self):
        return self.role == 'advisor'
    
    @property
    def is_seller(self):
        return self.role == 'seller'
    
    @property
    def is_client_user(self):
        return self.role == 'client'


class UserProfile(models.Model):
    """Perfil de usuario extendido"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Usuario"
    )
    bio = models.TextField(
        blank=True,
        verbose_name="Biografía"
    )
    website = models.URLField(
        blank=True,
        verbose_name="Sitio web"
    )
    linkedin = models.URLField(
        blank=True,
        verbose_name="LinkedIn"
    )
    timezone = models.CharField(
        max_length=50,
        default='America/Bogota',
        verbose_name="Zona horaria"
    )
    language = models.CharField(
        max_length=10,
        default='es',
        verbose_name="Idioma"
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notificaciones por email"
    )
    sms_notifications = models.BooleanField(
        default=False,
        verbose_name="Notificaciones SMS"
    )
    
    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"


class Country(models.Model):
    """País."""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    iso2 = models.CharField(max_length=2, unique=True, verbose_name="ISO2")
    iso3 = models.CharField(max_length=3, blank=True, verbose_name="ISO3")
    phone_code = models.CharField(
        max_length=10, blank=True, verbose_name="Código telefónico"
    )

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ['name']

    def __str__(self):
        return self.name


class State(models.Model):
    """Estado / Departamento / Provincia."""
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE,
        related_name='states', verbose_name="País"
    )
    name = models.CharField(max_length=150, verbose_name="Nombre")
    iso2 = models.CharField(max_length=10, blank=True, verbose_name="ISO2")

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['name']

    def __str__(self):
        return self.name


class City(models.Model):
    """Ciudad."""
    state = models.ForeignKey(
        State, on_delete=models.CASCADE,
        related_name='cities', verbose_name="Departamento"
    )
    name = models.CharField(max_length=150, verbose_name="Nombre")

    class Meta:
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"
        ordering = ['name']

    def __str__(self):
        return self.name


class UserAddress(models.Model):
    """Direcciones del usuario (puede tener varias)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name="Usuario"
    )
    label = models.CharField(
        max_length=50,
        default='Casa',
        verbose_name="Etiqueta",
        help_text="Ej: Casa, Oficina, Bodega…"
    )
    address = models.CharField(
        max_length=255,
        verbose_name="Dirección"
    )
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="País"
    )
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Departamento"
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Ciudad"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código postal"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Dirección principal"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        parts = [self.label, self.address]
        if self.city:
            parts.append(str(self.city))
        return ': '.join(parts[:2])

    def save(self, *args, **kwargs):
        if self.is_default:
            UserAddress.objects.filter(
                user=self.user, is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
