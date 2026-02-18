from decimal import Decimal
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Order
from apps.core.emails import (
    send_order_confirmation,
    send_order_shipped,
    send_order_delivered,
    send_admin_notification,
)


def _fmt_money(value: Decimal) -> str:
    try:
        return f"${value:,.0f}".replace(",", ".")
    except Exception:
        return str(value)


def _items_payload(order: Order):
    return [
        {
            "name": it.description,
            "qty": it.quantity,
            "total": _fmt_money(it.subtotal),
        }
        for it in order.items.all()
    ]


@receiver(pre_save, sender=Order)
def _store_prev_order_state(sender, instance: Order, **kwargs):
    if instance.pk:
        try:
            prev = Order.objects.get(pk=instance.pk)
            instance._old_status = prev.status
            instance._old_payment_status = prev.payment_status
        except Order.DoesNotExist:
            instance._old_status = None
            instance._old_payment_status = None
    else:
        instance._old_status = None
        instance._old_payment_status = None


@receiver(post_save, sender=Order)
def _send_order_emails(sender, instance: Order, created: bool, **kwargs):
    email = (instance.customer_email or "").strip()
    if not email:
        return

    old_status = getattr(instance, "_old_status", None)
    old_payment = getattr(instance, "_old_payment_status", None)

    try:
        # URL absoluta para dashboard si se configuró SITE_URL
        base = (getattr(settings, "SITE_URL", "") or "").rstrip("/")
        admin_path = f"/dashboard/ordenes/{instance.pk}/"
        admin_url = f"{base}{admin_path}" if base else admin_path

        if instance.payment_status == "approved" and old_payment != "approved":
            send_order_confirmation(
                to=email,
                order_number=instance.number,
                items=_items_payload(instance),
                order_total=_fmt_money(instance.total),
                view_order_url=None,
                billing_name=instance.customer_name,
                shipping_address=instance.customer_address,
            )
            # Notificación admin
            send_admin_notification(
                title=f"Pago aprobado • {instance.number}",
                body=(
                    f"Cliente: {instance.customer_name} <{instance.customer_email}>\n"
                    f"Total: {_fmt_money(instance.total)}\n"
                    f"Método: {instance.payment_method or ''}"
                ),
                cta_url=admin_url,
                cta_label="Ver orden",
            )

        if instance.status == "shipped" and old_status != "shipped":
            send_order_shipped(
                to=email,
                order_number=instance.number,
            )
            send_admin_notification(
                title=f"Orden enviada • {instance.number}",
                body=f"Cliente: {instance.customer_name} <{instance.customer_email}>",
                cta_url=admin_url,
                cta_label="Ver orden",
            )

        if instance.status == "delivered" and old_status != "delivered":
            send_order_delivered(
                to=email,
                order_number=instance.number,
            )
            send_admin_notification(
                title=f"Orden entregada • {instance.number}",
                body=f"Cliente: {instance.customer_name} <{instance.customer_email}>",
                cta_url=admin_url,
                cta_label="Ver orden",
            )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Error enviando correos de orden")
