"""
Importa monitores desde el JSON generado por extract_lista_pdf (lista_*_monitores_precio_lista.json).

Crea la categoría "Monitores" (slug monitores, orden 0) si no existe y añade productos con
precio_venta, descripción e imagen desde data/pdf_assets/...

Uso:
  python manage.py import_monitors_lista
  python manage.py import_monitors_lista --json data/otro.json --dry-run
"""
import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.store.models import Product, ProductCategory


def _base_slug(name: str, precio_venta: int, pagina: int | None, index: int) -> str:
    return slugify(f"{name}-{precio_venta}-p{pagina or 0}-i{index}")[:220] or f"monitor-i{index}"


def _assign_slug(base: str) -> str:
    slug = base
    n = 2
    while Product.objects.filter(slug=slug).exists():
        suf = f"-{n}"
        slug = (base[: 220 - len(suf)] + suf)[:220]
        n += 1
    return slug


class Command(BaseCommand):
    help = "Inserta monitores desde JSON de lista PDF en la categoría Monitores."

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            type=str,
            default="data/lista_2026_03_30_productos_monitores_precio_lista.json",
            help="Ruta al JSON relativa al directorio del proyecto (BASE_DIR).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="No escribe en la base de datos ni copia archivos de imagen.",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            help="No crea filas cuyo slug determinístico ya exista (útil al repetir el comando).",
        )

    def handle(self, *args, **options):
        base: Path = Path(settings.BASE_DIR)
        json_path = base / options["json"]
        if not json_path.is_file():
            self.stderr.write(self.style.ERROR(f"No existe el archivo: {json_path}"))
            return

        raw = json_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        items = data.get("productos") or []
        if not items:
            self.stderr.write(self.style.WARNING("El JSON no tiene clave 'productos' o está vacía."))
            return

        dry = options["dry_run"]

        if dry:
            self.stdout.write(self.style.WARNING("MODO dry-run (sin cambios en BD)."))

        skip_existing = options["skip_existing"]
        cat = None
        if not dry:
            self.stdout.write("Importando en una sola transacción…")

        created_n = 0
        skipped_img = 0
        skipped_dup = 0

        def run_import() -> None:
            nonlocal cat, created_n, skipped_img, skipped_dup
            if not dry:
                cat, created = ProductCategory.objects.get_or_create(
                    slug="monitores",
                    defaults={
                        "name": "Monitores",
                        "icon": "fa-desktop",
                        "order": 0,
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS('Categoría "Monitores" creada (slug=monitores, orden=0).'))
                else:
                    self.stdout.write('Categoría "monitores" ya existe; se reutiliza.')

            base_resolved = base.resolve()

            for idx, row in enumerate(items):
                nombre = (row.get("nombre") or "Monitor")[:200]
                desc = (row.get("descripcion") or "")[:3500]
                try:
                    venta = int(row["precio_venta"])
                except (KeyError, TypeError, ValueError):
                    self.stderr.write(self.style.WARNING(f"[{idx}] Sin precio_venta válido, se omite: {nombre[:50]}"))
                    continue
                pagina = row.get("pagina_pdf")
                pnum = pagina if isinstance(pagina, int) else None
                imagen_rel = row.get("imagen")

                slug_base = _base_slug(nombre, venta, pnum, idx)
                if dry:
                    self.stdout.write(f"  [{idx + 1}] {slug_base} | {nombre[:60]}… | ${venta:,}")
                    created_n += 1
                    continue

                if skip_existing and Product.objects.filter(slug=slug_base).exists():
                    skipped_dup += 1
                    continue
                slug = _assign_slug(slug_base)
                price = Decimal(venta)

                prod = Product(
                    name=nombre,
                    slug=slug,
                    category=cat,
                    description=desc,
                    price=price,
                    icon="fa-desktop",
                    icon_color="text-slate-600",
                    stock=0,
                    is_active=True,
                    is_featured=False,
                )
                prod.save()

                if imagen_rel:
                    rel = imagen_rel.strip().lstrip("/\\")
                    img_path = (base / Path(rel)).resolve()
                    if base_resolved != img_path and base_resolved not in img_path.parents:
                        self.stderr.write(
                            self.style.WARNING(f"Imagen fuera del proyecto, se omite: {imagen_rel}")
                        )
                        skipped_img += 1
                    elif img_path.is_file():
                        with img_path.open("rb") as f:
                            prod.image.save(img_path.name, File(f), save=True)
                    else:
                        self.stderr.write(self.style.WARNING(f"No existe archivo: {img_path}"))
                        skipped_img += 1
                else:
                    skipped_img += 1

                created_n += 1

        if dry:
            run_import()
        else:
            with transaction.atomic():
                run_import()

        parts = [f"Listo: {created_n} producto(s) {'simulados' if dry else 'creados'}"]
        if skipped_dup:
            parts.append(f"omitidos (ya existían): {skipped_dup}")
        if skipped_img:
            parts.append(f"sin imagen o archivo faltante: {skipped_img}")
        self.stdout.write(self.style.SUCCESS(" | ".join(parts)))
