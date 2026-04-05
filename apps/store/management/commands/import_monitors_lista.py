"""
Importa monitores desde el JSON generado por extract_lista_pdf (lista_*_monitores_precio_lista.json).

El campo "nombre" del JSON suele ser una línea suelta del PDF (p. ej. "sRGB 99%"); el script
deduce un título legible desde "descripcion" (Monitor: …, NITRO …, modelo VG/KA/…, etc.),
añade al texto los precios lista/venta y la fuente, y copia la imagen.

Uso:
  python manage.py import_monitors_lista
  python manage.py import_monitors_lista --json data/otro.json --dry-run
  python manage.py import_monitors_lista --excluir-equipos
"""
from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.store.models import Product, ProductCategory


def _clean_title(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s.strip(" ,.;:'\"'").strip()


def _is_junk_nombre(n: str) -> bool:
    n = (n or "").strip()
    if len(n) < 5:
        return True
    low = n.lower()
    if re.match(
        r"^(srgb|tipo de panel|vesa\s*:|altura|respuesta de|250 cd|hdmi|"
        r"\+ audio|fuente de poder|equipos power|r\d{4,}\s|"
        r"16gb\s*/?\s*512|ak2f1ut|'?\s*hdmi)",
        low,
    ):
        return True
    if re.match(r"^[\d.,]+[\"”\']?\s*$", n):
        return True
    return False


def _title_from_monitor_colon(desc: str) -> str | None:
    d = desc or ""
    m = re.search(r"(?is)Monitor\s*:\s*(.+?)(?=\s+EQUIPO\s+R\d|\s+Chasis:|\s+TARJETA\s+DE\s+VIDEO|\s+REFRIGERACION\b|\s+ALMACENAMIENTO:|\s+MEMORIA:|\s+Board:|\s+\(\d+\)\s+B/|\n|$)", d)
    if m:
        t = _clean_title(m.group(1))
        if len(t) >= 6:
            return t[:200]
    m = re.search(r"(?is)MONITOR\s*:\s*(.+?)(?=\s+PUERTOS|\s+CPU\s|\s+Soporte\s+VESA|\n|$)", d)
    if m:
        t = _clean_title(m.group(1))
        if len(t) >= 8:
            return t[:200]
    return None


def _title_from_brand_models(desc: str) -> str | None:
    d = desc or ""
    patterns = (
        r"(?is)\b(NITRO\s+CURVO\s+[^.\n]{8,75}?)(?=\s+Tipo de panel|\s+1ms|\s+2K|\s+UM\.|$)",
        r"(?is)\b(NITRO\s+[\d.,]+[”“\"']?\s*[A-Z]{1,3}\d[A-Za-z0-9\-]{0,18})(?=\s+Tipo|\s+Tecnolog|\s+Resoluci|\s+sRGB|\s+\d+Hz|$)",
        r"(?is)\b(TUF\s+Gaming\s+[A-Z0-9]{2,}[A-Za-z0-9\-]{2,32})",
        r"(?is)\b(ESCRITORIO\s+GAMER\s+[^\n]{12,80}?)(?=\s+Tipo de panel|\s+\d+ms|\s+\d+Hz|$)",
        r"(?is)\b(Monitor\s+HP\s+[^.\n]{10,90})",
    )
    for pat in patterns:
        m = re.search(pat, d)
        if m:
            t = _clean_title(m.group(1))
            if len(t) >= 10 and not _is_junk_nombre(t):
                return t[:200]
    m = re.search(
        r"(?i)^\s*([\d.,]+[”“\"']?\s*(?:NITRO\s+[\w]+|VA\d\w+|VG\d\w+|VP\d\w+|KA\d\w+|KG\d\w+|ED\d\w+|XZ\d\w+|XV\d\w+|MP\d\w+))",
        d,
    )
    if m:
        t = _clean_title(m.group(1))
        if len(t) >= 8:
            return t[:200]
    return None


def _title_from_desc_cut(desc: str) -> str | None:
    d = re.sub(r"\s+", " ", (desc or "").strip())
    if len(d) < 15:
        return None
    for stop in (
        " Tipo de panel:",
        " Frecuencia de actualización",
        " Acer VisionCare",
        " AMD Freesync",
        " AMD FreeSync",
        " Tiempo de respuesta",
        " 180Hz",
        " 200Hz",
        " 146Hz",
        " 144Hz",
        " 120Hz",
        " 1ms",
        " PIVOT ",
        " Pivote ",
    ):
        i = d.find(stop)
        if 20 <= i <= 160:
            return _clean_title(d[:i])[:200]
    return _clean_title(d[:100])[:200] if d else None


def derive_display_name(nombre: str, descripcion: str) -> str:
    for fn in (_title_from_monitor_colon, _title_from_brand_models, _title_from_desc_cut):
        t = fn(descripcion)
        if t:
            return t
    n = _clean_title(nombre)
    if n and not _is_junk_nombre(n):
        return n[:200]
    tail = _clean_title((descripcion or "")[:150])
    return (tail[:200] if tail else n[:200] or "Monitor")[:200]


def looks_like_pc_armado(descripcion: str) -> bool:
    """True si el bloque parece PC completo (chasis + CPU), no solo monitor."""
    d = descripcion or ""
    if not re.search(r"(?i)chasis\s*:", d):
        return False
    if not re.search(r"(?i)procesador\s*:", d):
        return False
    return True


def build_body_description(
    fuente: str,
    row: dict,
    original_desc: str,
) -> str:
    compra = row.get("precio_compra")
    venta = row.get("precio_venta")
    pag = row.get("pagina_pdf")
    raw_nombre = (row.get("nombre") or "").strip()
    lines = [
        f"Lista PDF: {fuente}" + (f" · página {pag}" if pag is not None else ""),
        f"Precio lista (COP): {compra:,}".replace(",", ".") if isinstance(compra, int) else "",
        f"Precio venta sugerido (COP): {venta:,}".replace(",", ".") if isinstance(venta, int) else "",
    ]
    if raw_nombre and _is_junk_nombre(raw_nombre):
        lines.append(f"Referencia PDF (línea automática): {raw_nombre}")
    header = "\n".join(x for x in lines if x)
    body = (original_desc or "").strip()
    return f"{header}\n\n---\n\n{body}" if body else header


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
        parser.add_argument(
            "--excluir-equipos",
            action="store_true",
            help="Omite ítems que parecen PC armado (Chasis: + Procesador: en la descripción).",
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
        excluir_equipos = options["excluir_equipos"]
        fuente_pdf = (data.get("fuente") or json_path.name).strip()
        cat = None
        if not dry:
            self.stdout.write("Importando en una sola transacción…")

        created_n = 0
        skipped_img = 0
        skipped_dup = 0
        skipped_equipos = 0

        def run_import() -> None:
            nonlocal cat, created_n, skipped_img, skipped_dup, skipped_equipos
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
                raw_desc = (row.get("descripcion") or "").strip()
                if excluir_equipos and looks_like_pc_armado(raw_desc):
                    skipped_equipos += 1
                    if dry:
                        self.stdout.write(
                            self.style.NOTICE(f"  [{idx + 1}] omitido (PC armado): {row.get('nombre', '')[:50]}")
                        )
                    continue

                nombre_pdf = row.get("nombre") or "Monitor"
                display_name = derive_display_name(nombre_pdf, raw_desc)[:200]
                desc = build_body_description(fuente_pdf, row, raw_desc)[:3500]
                try:
                    venta = int(row["precio_venta"])
                except (KeyError, TypeError, ValueError):
                    self.stderr.write(
                        self.style.WARNING(f"[{idx}] Sin precio_venta válido, se omite: {display_name[:50]}")
                    )
                    continue
                pagina = row.get("pagina_pdf")
                pnum = pagina if isinstance(pagina, int) else None
                imagen_rel = row.get("imagen")

                slug_base = _base_slug(display_name, venta, pnum, idx)
                if dry:
                    self.stdout.write(
                        f"  [{idx + 1}] {display_name[:70]} | ${venta:,} | slug: {slug_base[:50]}…"
                    )
                    created_n += 1
                    continue

                if skip_existing and Product.objects.filter(slug=slug_base).exists():
                    skipped_dup += 1
                    continue
                slug = _assign_slug(slug_base)
                price = Decimal(venta)

                prod = Product(
                    name=display_name,
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
        if skipped_equipos:
            parts.append(f"omitidos (equipos PC): {skipped_equipos}")
        if skipped_dup:
            parts.append(f"omitidos (ya existían): {skipped_dup}")
        if skipped_img:
            parts.append(f"sin imagen o archivo faltante: {skipped_img}")
        self.stdout.write(self.style.SUCCESS(" | ".join(parts)))
