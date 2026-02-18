from django.core.mail import EmailMessage, get_connection
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Envía un correo de prueba usando parámetros SMTP pasados por CLI (no modifica settings.py)."

    def add_arguments(self, parser):
        parser.add_argument("to_email", help="Correo de destino para la prueba")
        parser.add_argument("host", help="SMTP host, p. ej. mail.ejemplo.com")
        parser.add_argument("port", type=int, help="SMTP port, p. ej. 465 o 587")
        parser.add_argument("username", help="SMTP username")
        parser.add_argument("password", help="SMTP password")
        parser.add_argument("from_email", help="Dirección FROM, p. ej. 'Nombre <soporte@ejemplo.com>'")
        parser.add_argument("--use-ssl", action="store_true", default=False, help="Usar SSL (modo SMTPS, típico en 465)")
        parser.add_argument("--use-tls", action="store_true", default=False, help="Usar STARTTLS (típico en 587)")
        parser.add_argument("--subject", default="Prueba de correo", help="Asunto del correo")
        parser.add_argument("--body", default="Este es un correo de prueba de Megadominio.", help="Cuerpo del correo")
        parser.add_argument("--timeout", type=int, default=30, help="Timeout de conexión en segundos")

    def handle(self, *args, **opts):
        to_email = opts["to_email"]
        host = opts["host"]
        port = opts["port"]
        username = opts["username"]
        password = opts["password"]
        from_email = opts["from_email"]
        use_ssl = bool(opts["use_ssl"]) and not bool(opts["use_tls"])  # mutuamente excluyentes
        use_tls = bool(opts["use_tls"]) and not bool(opts["use_ssl"])  # preferir uno u otro
        subject = opts["subject"]
        body = opts["body"]
        timeout = opts["timeout"]

        if not to_email or "@" not in to_email:
            raise CommandError("'to_email' no es un correo válido")

        try:
            connection = get_connection(
                backend="django.core.mail.backends.smtp.EmailBackend",
                host=host,
                port=port,
                username=username,
                password=password,
                use_tls=use_tls,
                use_ssl=use_ssl,
                timeout=timeout,
            )

            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=[to_email],
                connection=connection,
            )
            sent = msg.send(fail_silently=False)
            if sent:
                self.stdout.write(self.style.SUCCESS("Correo de prueba enviado correctamente"))
            else:
                raise CommandError("No se pudo enviar el correo (send() devolvió 0)")
        except Exception as e:
            raise CommandError(f"Error enviando correo: {e}")
