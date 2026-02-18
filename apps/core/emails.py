from typing import Iterable, Mapping, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_html_email(
    subject: str,
    template: str,
    context: Optional[Mapping] = None,
    to: Optional[Iterable[str]] = None,
    from_email: Optional[str] = None,
    cc: Optional[Iterable[str]] = None,
    bcc: Optional[Iterable[str]] = None,
    reply_to: Optional[Iterable[str]] = None,
    headers: Optional[Mapping[str, str]] = None,
    attachments: Optional[Iterable] = None,
) -> int:
    ctx = dict(context or {})
    if "site_name" not in ctx:
        ctx["site_name"] = getattr(settings, "SITE_NAME", "Megadominio")
    if "brand_name" not in ctx:
        ctx["brand_name"] = ctx["site_name"]

    html = render_to_string(template, ctx)
    text = strip_tags(html)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=from_email or getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=list(to or []),
        cc=list(cc or []),
        bcc=list(bcc or []),
        reply_to=list(reply_to or []),
        headers=dict(headers or {}),
    )

    if attachments:
        for a in attachments:
            msg.attach(a)

    msg.attach_alternative(html, "text/html")
    return msg.send()


def send_account_confirmation(to: str, activation_url: str, user=None, subject: Optional[str] = None) -> int:
    return send_html_email(
        subject or "Confirma tu cuenta",
        "emails/account_confirmation.html",
        {"activation_url": activation_url, "user": user},
        [to],
    )


def send_order_confirmation(
    to: str,
    order_number: str,
    items: Optional[Iterable[Mapping]] = None,
    order_total: Optional[str] = None,
    view_order_url: Optional[str] = None,
    billing_name: Optional[str] = None,
    shipping_address: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    ctx = {
        "order_number": order_number,
        "items": list(items or []),
        "order_total": order_total,
        "view_order_url": view_order_url,
        "billing_name": billing_name,
        "shipping_address": shipping_address,
    }
    return send_html_email(
        subject or f"Confirmación de compra #{order_number}",
        "emails/order_confirmation.html",
        ctx,
        [to],
    )


def send_order_shipped(
    to: str,
    order_number: str,
    carrier: Optional[str] = None,
    tracking_number: Optional[str] = None,
    tracking_url: Optional[str] = None,
    estimated_delivery: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    ctx = {
        "order_number": order_number,
        "carrier": carrier,
        "tracking_number": tracking_number,
        "tracking_url": tracking_url,
        "estimated_delivery": estimated_delivery,
    }
    return send_html_email(
        subject or f"Tu pedido {order_number} fue despachado",
        "emails/order_shipped.html",
        ctx,
        [to],
    )


def send_order_delivered(
    to: str,
    order_number: str,
    rate_url: Optional[str] = None,
    view_order_url: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    ctx = {"order_number": order_number, "rate_url": rate_url, "view_order_url": view_order_url}
    return send_html_email(
        subject or f"Pedido {order_number} entregado",
        "emails/order_delivered.html",
        ctx,
        [to],
    )


def send_invoice_due_soon(
    to: str,
    invoice_number: str,
    due_date: str,
    amount_due: str,
    pay_url: Optional[str] = None,
    invoice_url: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    ctx = {
        "invoice_number": invoice_number,
        "due_date": due_date,
        "amount_due": amount_due,
        "pay_url": pay_url,
        "invoice_url": invoice_url,
    }
    return send_html_email(
        subject or f"Recordatorio: factura {invoice_number} vence pronto",
        "emails/invoice_due_soon.html",
        ctx,
        [to],
    )


def send_invoice_overdue(
    to: str,
    invoice_number: str,
    due_date: str,
    amount_due: str,
    pay_url: Optional[str] = None,
    help_url: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    ctx = {
        "invoice_number": invoice_number,
        "due_date": due_date,
        "amount_due": amount_due,
        "pay_url": pay_url,
        "help_url": help_url,
    }
    return send_html_email(
        subject or f"Factura {invoice_number} vencida",
        "emails/invoice_overdue.html",
        ctx,
        [to],
    )


def send_subscription_welcome(
    to: str,
    plan_name: str,
    next_billing_date: Optional[str] = None,
    manage_url: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    ctx = {"plan_name": plan_name, "next_billing_date": next_billing_date, "manage_url": manage_url}
    return send_html_email(
        subject or f"Bienvenido(a) a tu suscripción {plan_name}",
        "emails/subscription_welcome.html",
        ctx,
        [to],
    )


def send_subscription_canceled(
    to: str,
    end_date: Optional[str] = None,
    resume_url: Optional[str] = None,
    feedback_url: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    ctx = {"end_date": end_date, "resume_url": resume_url, "feedback_url": feedback_url}
    return send_html_email(
        subject or "Tu suscripción fue cancelada",
        "emails/subscription_canceled.html",
        ctx,
        [to],
    )


def send_generic_notification(
    to: str,
    title: str,
    body: Optional[str] = None,
    body_html: Optional[str] = None,
    cta_url: Optional[str] = None,
    cta_label: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    ctx = {
        "title": title,
        "body": body,
        "body_html": body_html,
        "cta_url": cta_url,
        "cta_label": cta_label,
    }
    return send_html_email(
        subject or title,
        "emails/generic_notification.html",
        ctx,
        [to],
    )


def admin_recipients() -> list[str]:
    emails: list[str] = []
    try:
        # Django ADMINS: list of (name, email)
        admins = getattr(settings, "ADMINS", ()) or ()
        for _name, mail in admins:
            if mail:
                emails.append(str(mail))
    except Exception:
        pass

    # Additional fallbacks
    extra = []
    for key in ("ADMIN_EMAILS", "DEFAULT_ADMIN_EMAIL"):
        val = getattr(settings, key, None)
        if isinstance(val, (list, tuple)):
            extra.extend([str(v) for v in val if v])
        elif isinstance(val, str) and val:
            extra.append(val)
    for k in ("SERVER_EMAIL", "EMAIL_HOST_USER"):
        v = getattr(settings, k, None)
        if isinstance(v, str) and v:
            extra.append(v)

    # De-dup
    for e in extra:
        if e and e not in emails:
            emails.append(e)
    return emails


def send_admin_notification(
    title: str,
    *,
    body: Optional[str] = None,
    body_html: Optional[str] = None,
    cta_url: Optional[str] = None,
    cta_label: Optional[str] = None,
    subject: Optional[str] = None,
) -> int:
    recipients = admin_recipients()
    if not recipients:
        return 0
    ctx = {
        "title": title,
        "body": body,
        "body_html": body_html,
        "cta_url": cta_url,
        "cta_label": cta_label,
    }
    return send_html_email(
        subject or title,
        "emails/generic_notification.html",
        ctx,
        recipients,
    )
