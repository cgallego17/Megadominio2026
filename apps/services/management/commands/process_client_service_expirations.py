from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.emails import send_admin_notification, send_generic_notification
from apps.services.models import ClientService


class Command(BaseCommand):
    help = (
        "Procesa vencimientos de servicios: "
        "envía avisos a 15 y 3 días, y deshabilita servicios vencidos."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="No envía correos ni guarda cambios; solo simula.",
        )

    def handle(self, *args, **options):
        dry_run = bool(options.get("dry_run"))
        today = timezone.localdate() if settings.USE_TZ else date.today()
        now = timezone.now()
        total_15 = 0
        total_3 = 0
        total_expired = 0

        qs_base = ClientService.objects.select_related("client", "service").filter(
            status="active",
            end_date__isnull=False,
        )

        total_15 += self._notify_before_days(
            qs=qs_base,
            today=today,
            now=now,
            days=15,
            field_name="reminder_15_sent_at",
            dry_run=dry_run,
        )
        total_3 += self._notify_before_days(
            qs=qs_base,
            today=today,
            now=now,
            days=3,
            field_name="reminder_3_sent_at",
            dry_run=dry_run,
        )
        total_expired += self._disable_expired(
            qs=qs_base,
            today=today,
            now=now,
            dry_run=dry_run,
        )

        msg = (
            f"Proceso finalizado. "
            f"Avisos 15 días: {total_15} | "
            f"Avisos 3 días: {total_3} | "
            f"Servicios deshabilitados: {total_expired}"
        )
        self.stdout.write(self.style.SUCCESS(msg))

    def _notify_before_days(self, *, qs, today, now, days, field_name, dry_run):
        target_date = today + timedelta(days=days)
        items = qs.filter(end_date=target_date, **{f"{field_name}__isnull": True})
        count = 0
        for cs in items:
            client_email = (cs.client.email or "").strip()
            if not client_email:
                continue

            service_name = cs.service.name
            client_name = cs.client.name
            end_date_str = cs.end_date.strftime("%d/%m/%Y")
            manage_url = self._build_url("/mi-cuenta/servicios/")
            admin_url = self._build_url(f"/dashboard/servicios-clientes/{cs.pk}/")

            subject = f"Tu servicio {service_name} vence en {days} días"
            body = (
                f"Hola {client_name},\n\n"
                f"Te recordamos que tu servicio '{service_name}' "
                f"vence el {end_date_str} (en {days} días).\n"
                f"Por favor revisa tu servicio para gestionar la renovación."
            )
            admin_body = (
                f"Cliente: {client_name} <{client_email}>\n"
                f"Servicio: {service_name}\n"
                f"Vence: {end_date_str}\n"
                f"Aviso enviado: {days} días antes"
            )

            if dry_run:
                self.stdout.write(
                    f"[DRY] Aviso {days}d -> {client_email} | {service_name}"
                )
                count += 1
                continue

            send_generic_notification(
                to=client_email,
                title=subject,
                body=body,
                cta_url=manage_url,
                cta_label="Ver mis servicios" if manage_url else None,
                subject=subject,
            )
            send_admin_notification(
                title=f"Recordatorio {days}d enviado: {service_name}",
                body=admin_body,
                cta_url=admin_url,
                cta_label="Ver servicio" if admin_url else None,
            )
            setattr(cs, field_name, now)
            cs.save(update_fields=[field_name, "updated_at"])
            count += 1
        return count

    def _disable_expired(self, *, qs, today, now, dry_run):
        # Se deshabilita cuando ya pasó la fecha de fin.
        items = qs.filter(end_date__lt=today)
        count = 0
        for cs in items:
            client_email = (cs.client.email or "").strip()
            service_name = cs.service.name
            client_name = cs.client.name
            end_date_str = cs.end_date.strftime("%d/%m/%Y")
            manage_url = self._build_url("/mi-cuenta/servicios/")
            admin_url = self._build_url(f"/dashboard/servicios-clientes/{cs.pk}/")

            if dry_run:
                self.stdout.write(
                    f"[DRY] Deshabilitar vencido -> {client_name} | {service_name}"
                )
                count += 1
                continue

            cs.status = "inactive"
            update_fields = ["status", "auto_disabled_at", "updated_at"]
            cs.auto_disabled_at = now

            if cs.expired_notified_at is None:
                subject = f"Servicio deshabilitado por vencimiento: {service_name}"
                body = (
                    f"Hola {client_name},\n\n"
                    f"Tu servicio '{service_name}' fue deshabilitado porque "
                    f"venció el {end_date_str}.\n"
                    f"Contáctanos para renovarlo y reactivarlo."
                )
                admin_body = (
                    f"Cliente: {client_name} <{client_email or 'sin email'}>\n"
                    f"Servicio: {service_name}\n"
                    f"Vencimiento: {end_date_str}\n"
                    f"Estado nuevo: Inactivo (automático)"
                )

                if client_email:
                    send_generic_notification(
                        to=client_email,
                        title=subject,
                        body=body,
                        cta_url=manage_url,
                        cta_label="Ver mis servicios" if manage_url else None,
                        subject=subject,
                    )
                send_admin_notification(
                    title=f"Servicio deshabilitado por vencimiento: {service_name}",
                    body=admin_body,
                    cta_url=admin_url,
                    cta_label="Ver servicio" if admin_url else None,
                )
                cs.expired_notified_at = now
                update_fields.append("expired_notified_at")

            cs.save(update_fields=update_fields)
            count += 1
        return count

    def _build_url(self, path):
        site_url = (getattr(settings, "SITE_URL", "") or "").rstrip("/")
        if not site_url:
            return None
        if not site_url.startswith(("http://", "https://")):
            site_url = f"https://{site_url}"
        return f"{site_url}{path}"
