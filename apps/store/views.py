import json
import hashlib
import hmac
import logging
import requests
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Product, Order, OrderItem
from apps.core.emails import send_payment_failed, send_admin_notification

logger = logging.getLogger(__name__)


# Slugs de planes digitales (no generan costo de envío)
DIGITAL_PLAN_SLUGS = {
    'presencia-web', 'corporativo', 'e-commerce', 'empresarial',
    'hosting-basico', 'hosting-pro', 'email-profesional', 'cloud-empresarial',
    'seo-starter', 'social-media', 'google-ads', 'marketing-360',
    'e-commerce-basico', 'e-commerce-pro', 'e-commerce-avanzado',
    'marketplace',
    'instalacion-basica', 'seguridad-backup', 'velocidad-seo',
    'soporte-mensual',
}


def _get_next_order_number():
    """Genera el siguiente número de orden secuencial."""
    last = Order.objects.order_by('-id').first()
    if last and last.number.startswith('ORD-'):
        try:
            num = int(last.number.split('-')[1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f'ORD-{num:05d}'


def _wompi_api_base():
    """Retorna la URL base de la API de Wompi."""
    if settings.WOMPI_SANDBOX:
        return 'https://sandbox.wompi.co/v1'
    return 'https://production.wompi.co/v1'


def _get_acceptance_token():
    """Obtiene el acceptance token de Wompi (merchants endpoint)."""
    url = f'{_wompi_api_base()}/merchants/{settings.WOMPI_PUBLIC_KEY}'
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data['data']['presigned_acceptance']['acceptance_token']
    except Exception:
        logger.exception('Error obteniendo acceptance token de Wompi')
        return ''


def _verify_wompi_signature(event_body, signature_header):
    """Verifica la firma del webhook de Wompi."""
    if not settings.WOMPI_EVENTS_SECRET:
        return True
    try:
        props = event_body.get('signature', {}).get('properties', [])
        ts = event_body.get('timestamp', '')
        tx_data = event_body.get('data', {}).get('transaction', {})
        values = ''
        for prop in props:
            values += str(tx_data.get(prop, ''))
        values += str(ts)
        values += settings.WOMPI_EVENTS_SECRET
        computed = hashlib.sha256(values.encode()).hexdigest()
        received = event_body.get('signature', {}).get('checksum', '')
        return hmac.compare_digest(computed, received)
    except Exception:
        logger.exception('Error verificando firma Wompi')
        return False


def _verify_transaction(transaction_id):
    """Verifica una transacción directamente con la API de Wompi."""
    url = f'{_wompi_api_base()}/transactions/{transaction_id}'
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json().get('data', {})
    except Exception:
        logger.exception('Error verificando transacción Wompi')
    return None


# ═══════════════════════════════════════════════════════════════
# CHECKOUT
# ═══════════════════════════════════════════════════════════════

def checkout(request):
    """
    POST: Recibe carrito desde JS, crea orden, retorna datos para Wompi.
    GET:  Muestra página de checkout.
    """
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        cart_items = body.get('items', [])
        customer = body.get('customer', {})

        if not cart_items:
            return JsonResponse({'error': 'Carrito vacío'}, status=400)

        name = customer.get('name', '').strip()
        email = customer.get('email', '').strip()
        phone = customer.get('phone', '').strip()
        address = customer.get('address', '').strip()
        country = customer.get('country', '').strip()
        state = customer.get('state', '').strip()
        city = customer.get('city', '').strip()
        doc_type = customer.get('doc_type', '').strip()
        document = customer.get('document', '').strip()

        if not name or not email or not phone or not document:
            return JsonResponse(
                {'error': 'Nombre, email, teléfono y documento requeridos'},
                status=400
            )

        # Determine if all items are digital plans
        all_digital = True
        for it in cart_items:
            slug_val = str(it.get('id', '')).strip()
            if slug_val not in DIGITAL_PLAN_SLUGS:
                all_digital = False
                break

        # Create order
        order = Order(
            number=_get_next_order_number(),
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            customer_address=address,
            customer_country=country,
            customer_state=state,
            customer_city=city,
            customer_doc_type=doc_type,
            customer_document=document,
            status='pending',
            payment_status='pending',
            shipping_cost=Decimal('0') if all_digital else Decimal('12000'),
        )
        if request.user.is_authenticated:
            order.created_by = request.user
        order.save()

        # Create order items
        subtotal = Decimal('0')
        for item in cart_items:
            slug = item.get('id', '')
            qty = int(item.get('qty', 1))
            product = Product.objects.filter(
                slug=slug, is_active=True
            ).first()
            if product:
                line_price = product.price
                item_name = product.name
            else:
                line_price = Decimal(str(item.get('price', 0)))
                item_name = item.get('name', 'Producto')

            oi = OrderItem.objects.create(
                order=order,
                product=product,
                description=item_name,
                quantity=qty,
                unit_price=line_price,
            )
            subtotal += oi.subtotal

        order.subtotal = subtotal
        order.total = subtotal + order.shipping_cost - order.discount
        order.save(update_fields=['subtotal', 'total'])

        # Wompi amount in cents (COP)
        amount_cents = int(order.total * 100)

        return JsonResponse({
            'order_id': order.pk,
            'order_number': order.number,
            'amount_cents': amount_cents,
            'currency': settings.WOMPI_CURRENCY,
            'public_key': settings.WOMPI_PUBLIC_KEY,
            'reference': order.number,
            'redirect_url': request.build_absolute_uri(
                f'/tienda/checkout/resultado/?ref={order.number}'
            ),
            'customer_email': email,
            'customer_name': name,
            'customer_phone': phone,
        })

    # GET — render checkout page
    from apps.accounts.models import Country, UserAddress
    countries = Country.objects.all()
    iso_map = {c.pk: c.iso2 for c in countries}

    # Pre-fill data for authenticated users
    prefill = {}
    if request.user.is_authenticated:
        u = request.user
        prefill['name'] = u.get_full_name() or ''
        prefill['email'] = u.email or ''
        prefill['phone'] = getattr(u, 'phone', '') or ''
        # Try to get default address
        addr = UserAddress.objects.filter(
            user=u, is_default=True
        ).first()
        if not addr:
            addr = UserAddress.objects.filter(user=u).first()
        if addr:
            prefill['address'] = addr.address or ''
            prefill['country_id'] = addr.country_id or ''
            prefill['state_id'] = addr.state_id or ''
            prefill['city_id'] = addr.city_id or ''

    return render(request, 'core/checkout.html', {
        'wompi_public_key': settings.WOMPI_PUBLIC_KEY,
        'wompi_currency': settings.WOMPI_CURRENCY,
        'wompi_sandbox': settings.WOMPI_SANDBOX,
        'countries': countries,
        'iso_map': iso_map,
        'prefill': prefill,
        'digital_plan_slugs': sorted(list(DIGITAL_PLAN_SLUGS)),
    })


def checkout_result(request):
    """
    Página de resultado post-pago. Wompi redirige aquí.
    Verifica el estado de la transacción con la API de Wompi.
    """
    ref = request.GET.get('ref', '')
    transaction_id = request.GET.get('id', '')

    order = get_object_or_404(Order, number=ref)

    status_display = 'pending'
    tx_data = None

    if transaction_id:
        tx_data = _verify_transaction(transaction_id)
        if tx_data:
            wompi_status = tx_data.get('status', '')
            order.wompi_transaction_id = transaction_id
            order.payment_method = tx_data.get(
                'payment_method_type', ''
            )

            if wompi_status == 'APPROVED':
                order.payment_status = 'approved'
                order.status = 'confirmed'
                order.paid_at = timezone.now()
                status_display = 'approved'
            elif wompi_status == 'DECLINED':
                order.payment_status = 'declined'
                status_display = 'declined'
            elif wompi_status == 'VOIDED':
                order.payment_status = 'voided'
                status_display = 'voided'
            elif wompi_status == 'ERROR':
                order.payment_status = 'error'
                status_display = 'error'
            else:
                status_display = 'pending'

            order.save(update_fields=[
                'wompi_transaction_id', 'payment_status',
                'payment_method', 'status', 'paid_at',
            ])

    return render(request, 'core/checkout_result.html', {
        'order': order,
        'status': status_display,
        'transaction_id': transaction_id,
    })


# ═══════════════════════════════════════════════════════════════
# WEBHOOK WOMPI
# ═══════════════════════════════════════════════════════════════

@csrf_exempt
@require_POST
def wompi_webhook(request):
    """
    Recibe eventos de Wompi (transaction.updated).
    Verifica firma y actualiza la orden correspondiente.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid JSON')

    # Verify signature
    sig_header = request.headers.get('X-Event-Checksum', '')
    if not _verify_wompi_signature(body, sig_header):
        logger.warning('Wompi webhook: firma inválida')
        return HttpResponseBadRequest('Invalid signature')

    event_type = body.get('event', '')
    if event_type != 'transaction.updated':
        return JsonResponse({'status': 'ignored'})

    tx = body.get('data', {}).get('transaction', {})
    tx_id = tx.get('id', '')
    tx_status = tx.get('status', '')
    tx_reference = tx.get('reference', '')
    tx_method = tx.get('payment_method_type', '')

    if not tx_reference:
        return JsonResponse({'status': 'no reference'})

    try:
        order = Order.objects.get(number=tx_reference)
    except Order.DoesNotExist:
        logger.warning(f'Wompi webhook: orden no encontrada: {tx_reference}')
        return JsonResponse({'status': 'order not found'}, status=404)

    order.wompi_transaction_id = tx_id
    order.payment_method = tx_method

    if tx_status == 'APPROVED':
        order.payment_status = 'approved'
        order.status = 'confirmed'
        order.paid_at = timezone.now()
    elif tx_status == 'DECLINED':
        order.payment_status = 'declined'
        # Notificar fallo de pago al cliente y admin
        try:
            if order.customer_email:
                base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
                retry_url = f"{base}/tienda/" if base else '/tienda/'
                send_payment_failed(
                    to=order.customer_email,
                    order_number=order.number,
                    payment_method=order.payment_method,
                    retry_url=retry_url,
                    failure_reason='pago declinado',
                )
            base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
            admin_path = f"/dashboard/ordenes/{order.pk}/"
            admin_url = f"{base}{admin_path}" if base else admin_path
            send_admin_notification(
                title=f"Pago declinado • {order.number}",
                body=(
                    f"Cliente: {order.customer_name} <{order.customer_email}>\n"
                    f"Método: {order.payment_method or ''}"
                ),
                cta_url=admin_url,
                cta_label='Ver orden',
            )
        except Exception:
            logger.exception('Error enviando notificaciones de pago declinado')
    elif tx_status == 'VOIDED':
        order.payment_status = 'voided'
        try:
            if order.customer_email:
                base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
                retry_url = f"{base}/tienda/" if base else '/tienda/'
                send_payment_failed(
                    to=order.customer_email,
                    order_number=order.number,
                    payment_method=order.payment_method,
                    retry_url=retry_url,
                    failure_reason='pago anulado',
                )
            base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
            admin_path = f"/dashboard/ordenes/{order.pk}/"
            admin_url = f"{base}{admin_path}" if base else admin_path
            send_admin_notification(
                title=f"Pago anulado • {order.number}",
                body=f"Cliente: {order.customer_name} <{order.customer_email}>",
                cta_url=admin_url,
                cta_label='Ver orden',
            )
        except Exception:
            logger.exception('Error enviando notificaciones de pago anulado')
    elif tx_status == 'ERROR':
        order.payment_status = 'error'
        try:
            if order.customer_email:
                base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
                retry_url = f"{base}/tienda/" if base else '/tienda/'
                send_payment_failed(
                    to=order.customer_email,
                    order_number=order.number,
                    payment_method=order.payment_method,
                    retry_url=retry_url,
                    failure_reason='error en el pago',
                )
            base = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
            admin_path = f"/dashboard/ordenes/{order.pk}/"
            admin_url = f"{base}{admin_path}" if base else admin_path
            send_admin_notification(
                title=f"Error de pago • {order.number}",
                body=f"Cliente: {order.customer_name} <{order.customer_email}>",
                cta_url=admin_url,
                cta_label='Ver orden',
            )
        except Exception:
            logger.exception('Error enviando notificaciones de error de pago')

    order.save(update_fields=[
        'wompi_transaction_id', 'payment_status',
        'payment_method', 'status', 'paid_at',
    ])

    logger.info(
        f'Wompi webhook: orden {tx_reference} → {tx_status}'
    )
    return JsonResponse({'status': 'ok'})
