from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Quote
from apps.core.emails import send_admin_notification


@receiver(pre_save, sender=Quote)
def _store_prev_quote_state(sender, instance: Quote, **kwargs):
    if instance.pk:
        try:
            prev = Quote.objects.get(pk=instance.pk)
            instance._old_status = prev.status
        except Quote.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Quote)
def _notify_quote_events(sender, instance: Quote, created: bool, **kwargs):
    try:
        admin_url = None
        # Intentar armar URL del dashboard (ruta admin) sin request
        try:
            path = reverse('core:dashboard_quote_detail', args=[instance.pk])
            admin_url = path
        except Exception:
            admin_url = None

        # Notificar creación (cuando pasa a 'sent' desde vistas ya se notificó al cliente)
        if created:
            title = f"Nueva cotización creada • {instance.number}"
            body = (
                f"Cliente: {instance.client.name} <{instance.client.email}>\n"
                f"Estado: {instance.get_status_display()}"
            )
            send_admin_notification(
                title=title,
                body=body,
                cta_url=admin_url,
                cta_label='Ver cotización',
            )
            return

        old = getattr(instance, '_old_status', None)
        if old != instance.status:
            state = instance.get_status_display()
            title = f"Cotización {instance.number} → {state}"
            body = (
                f"Cliente: {instance.client.name} <{instance.client.email}>\n"
                f"Antes: {old or '-'} • Ahora: {instance.status}"
            )
            send_admin_notification(
                title=title,
                body=body,
                cta_url=admin_url,
                cta_label='Ver cotización',
            )
    except Exception:
        # Evitar que errores de correo afecten transacciones de BD
        import logging
        logging.getLogger(__name__).exception('Error notificando evento de cotización')
