from django.db import models


class HomeClientLogo(models.Model):
    name = models.CharField(max_length=120)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='logos/', blank=True, null=True)
    icon = models.CharField(
        max_length=64,
        blank=True,
        help_text=(
            "Clase de icono Font Awesome, por ejemplo 'fa-rocket'. "
            "Se usa si no se sube imagen."
        ),
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Logo de cliente (Home)'
        verbose_name_plural = 'Logos de clientes (Home)'

    def __str__(self):
        return self.name


class HomeTestimonial(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    company = models.CharField(max_length=160, blank=True)
    initials = models.CharField(
        max_length=4,
        blank=True,
        help_text='Iniciales para avatar si no hay imagen',
    )
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Testimonio (Home)'
        verbose_name_plural = 'Testimonios (Home)'

    def __str__(self):
        return f"{self.name} - {self.company or ''}"
