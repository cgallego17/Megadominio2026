from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.conf import settings

from .models import ClientService
from apps.core.emails import send_service_assigned_notification, send_admin_notification


@receiver(post_save, sender=ClientService)
def notify_client_service_assigned(sender, instance, created, **kwargs):
    """
    Envía notificación por correo al cliente cuando se le asigna un nuevo servicio.
    También notifica al administrador sobre la asignación.
    """
    if not created:
        # Solo notificamos cuando se crea un nuevo servicio, no en actualizaciones
        return

    # Verificamos que el cliente tenga email
    client_email = instance.client.email
    if not client_email:
        return

    try:
        # Formateamos los valores para el correo
        service_name = instance.service.name
        client_name = instance.client.name
        amount = f"${instance.monthly_price:,.0f}".replace(',', '.')
        billing_type = instance.get_billing_type_display()
        start_date = instance.start_date.strftime('%d/%m/%Y')
        
        # Valores opcionales
        end_date = instance.end_date.strftime('%d/%m/%Y') if instance.end_date else None
        renewal_price = None
        if instance.renewal_price and instance.renewal_price > 0:
            renewal_price = f"${instance.renewal_price:,.0f}".replace(',', '.')
        
        # URL para que el cliente vea sus servicios
        manage_url = None
        if hasattr(settings, 'SITE_URL') and settings.SITE_URL:
            manage_url = f"{settings.SITE_URL}/mi-cuenta/servicios/"
        
        # Enviamos el correo al cliente
        send_service_assigned_notification(
            to=client_email,
            service_name=service_name,
            amount=amount,
            billing_type=billing_type,
            start_date=start_date,
            client_name=client_name,
            renewal_price=renewal_price,
            end_date=end_date,
            manage_url=manage_url,
        )
        
        # Notificamos también al administrador
        admin_url = None
        if hasattr(settings, 'SITE_URL') and settings.SITE_URL:
            admin_url = f"{settings.SITE_URL}/dashboard/servicios-clientes/{instance.pk}/"
            
        send_admin_notification(
            title=f"Nuevo servicio asignado: {service_name}",
            body=(
                f"Cliente: {client_name}\n"
                f"Servicio: {service_name}\n"
                f"Valor: {amount}\n"
                f"Tipo: {billing_type}\n"
                f"Fecha inicio: {start_date}"
            ),
            cta_url=admin_url,
            cta_label="Ver detalle del servicio" if admin_url else None,
        )
    except Exception as e:
        # En caso de error, notificamos al admin pero no interrumpimos el flujo
        send_admin_notification(
            title="Error al enviar notificación de servicio asignado",
            body=f"Cliente: {instance.client.name}\nServicio: {instance.service.name}\nError: {str(e)}",
        )
