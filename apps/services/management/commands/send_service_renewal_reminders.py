from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from apps.services.models import ClientService
from apps.core.emails import send_service_renewal_reminder, admin_recipients, send_admin_notification


class Command(BaseCommand):
    help = (
        "Envía recordatorios de renovación para servicios de clientes. "
        "Se envían 3 recordatorios por servicio: 15, 7 y 1 día antes de la fecha de fin. "
        "Si renewal_price es 0, se usa monthly_price."
    )

    def add_arguments(self, parser):
        parser.add_argument('--days', nargs='*', type=int, default=[15, 7, 1],
                            help='Días antes de la fecha de fin para recordar (por defecto: 15 7 1)')
        parser.add_argument('--dry-run', action='store_true', default=False,
                            help='No envía correos, solo muestra qué se enviaría')

    def handle(self, *args, **opts):
        days_list = sorted(set(int(d) for d in (opts.get('days') or [15, 7, 1]) if int(d) > 0), reverse=True)
        dry = bool(opts.get('dry_run'))

        tz_now = timezone.localdate() if settings.USE_TZ else date.today()
        total = 0
        for d in days_list:
            target = tz_now + timedelta(days=d)
            # Tomamos servicios activos con end_date y que renovarán ese día
            qs = ClientService.objects.select_related('client', 'service').filter(
                status='active', end_date=target
            )
            for cs in qs:
                amount_num = cs.renewal_price or cs.monthly_price
                amount = f"${amount_num:,.0f}".replace(',', '.')
                billing_type = cs.get_billing_type_display()
                service_name = cs.service.name
                client_name = cs.client.name
                to_email = (cs.client.email or '').strip()
                manage_url = None
                pay_url = None
                if not to_email:
                    continue
                if dry:
                    self.stdout.write(f"[DRY] {to_email} • {service_name} • {target} • {amount}")
                    total += 1
                    continue
                try:
                    send_service_renewal_reminder(
                        to=to_email,
                        service_name=service_name,
                        renewal_date=target.strftime('%d/%m/%Y'),
                        amount=amount,
                        billing_type=billing_type,
                        client_name=client_name,
                        pay_url=pay_url,
                        manage_url=manage_url,
                    )
                    total += 1
                except Exception:
                    send_admin_notification(
                        title='Error enviando recordatorio de renovación',
                        body=(
                            f"Cliente: {client_name} <{to_email}>\n"
                            f"Servicio: {service_name}\n"
                            f"Fecha: {target}"
                        ),
                    )
        self.stdout.write(self.style.SUCCESS(f"Recordatorios procesados: {total}"))
