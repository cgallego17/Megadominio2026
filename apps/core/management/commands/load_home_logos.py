import os
import re
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max

from apps.core.models import HomeClientLogo


class Command(BaseCommand):
    help = "Copia imágenes desde rutas locales y crea entradas HomeClientLogo activas."

    def add_arguments(self, parser):
        parser.add_argument(
            "paths",
            nargs="+",
            help="Rutas absolutas a archivos de imagen (png, jpg, svg, etc.)",
        )

    def handle(self, *args, **options):
        paths = options["paths"]
        if not paths:
            raise CommandError("Debes proporcionar al menos una ruta de imagen.")

        agg = HomeClientLogo.objects.aggregate(max_order=Max("order"))
        current_order = agg["max_order"] or 0
        created = 0
        for p in paths:
            if not os.path.isabs(p):
                self.stderr.write(self.style.WARNING(f"Ruta no absoluta, se omite: {p}"))
                continue
            if not os.path.exists(p):
                self.stderr.write(self.style.ERROR(f"No existe el archivo: {p}"))
                continue

            base = os.path.basename(p)
            name_guess = os.path.splitext(base)[0]
            # limpieza del nombre: guiones/underscores -> espacios, compresión de espacios, capitalización
            name_guess = re.sub(r"[_-]+", " ", name_guess)
            name_guess = re.sub(r"\s+", " ", name_guess).strip().title()

            current_order += 1
            obj = HomeClientLogo(name=name_guess, is_active=True, order=current_order)
            with open(p, "rb") as fh:
                djf = File(fh, name=base)
                # FieldFile.save aplica upload_to en generate_filename
                obj.image.save(base, djf, save=False)
            obj.save()
            created += 1
            # Avoid non-ASCII symbols for Windows consoles
            self.stdout.write(self.style.SUCCESS(f"Creado: {obj.name} (order {obj.order})"))

        self.stdout.write(self.style.SUCCESS(f"Listo. Logos creados: {created}"))
