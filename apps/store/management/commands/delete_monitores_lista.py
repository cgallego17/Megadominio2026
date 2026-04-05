"""
Borra productos de la categoría de import_monitors_lista (slug: monitores).

No elimina la categoría, solo los Product con esa category.

Uso:
  python manage.py delete_monitores_lista
  python manage.py delete_monitores_lista --yes
"""
from django.core.management.base import BaseCommand

from apps.store.models import Product, ProductCategory


class Command(BaseCommand):
    help = 'Borra productos de la categoría "monitores" (slug monitores).'

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Confirmar borrado permanente de esos productos.",
        )

    def handle(self, *args, **options):
        cat = ProductCategory.objects.filter(slug="monitores").first()
        if not cat:
            self.stdout.write(
                self.style.WARNING('No existe categoría con slug "monitores".')
            )
            return

        qs = Product.objects.filter(category=cat)
        n = qs.count()
        if n == 0:
            self.stdout.write("No hay productos en la categoría Monitores.")
            return

        if not options["yes"]:
            self.stdout.write(
                f'Hay {n} producto(s) en "Monitores". '
                "Ejecuta con --yes para borrarlos:\n"
                "  python manage.py delete_monitores_lista --yes"
            )
            return

        _, detail = qs.delete()
        self.stdout.write(
            self.style.SUCCESS(f"Borrados {n} producto(s). Detalle: {detail}")
        )
