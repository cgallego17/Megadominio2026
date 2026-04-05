"""
Extrae productos (nombre, descripción, precio) del PDF de lista de precios.
Opcionalmente extrae imágenes incrustadas (PyMuPDF) y enlaza por página del PDF.

Uso:
  python scripts/extract_lista_pdf.py "ruta/al/archivo.pdf" [salida.json]
  python scripts/extract_lista_pdf.py "lista.pdf" out.json --sin-imagenes

Requiere: pip install pypdf pymupdf
"""
from __future__ import annotations

import json
import re
import sys
from io import BytesIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    from pypdf import PdfReader
except ImportError:
    print("Instala: pip install pypdf", file=sys.stderr)
    sys.exit(1)

# Sobre el precio de lista (compra) del PDF, para el JSON de monitores:
MARGEN_VENTA_SOBRE_COMPRA_COP = 100_000

PAGE_MARK_RE = re.compile(r"__PAGE_(\d+)__")
PAGE_LINE_RE = re.compile(r"^\s*__PAGE_\d+__\s*$")


def pdf_stem_slug(pdf_path: Path) -> str:
    s = re.sub(r"[^\w\-]+", "_", pdf_path.stem, flags=re.I)
    return (s.strip("_")[:80] or "lista").lower()


def pdf_to_text(path: Path) -> str:
    r = PdfReader(str(path))
    parts: list[str] = []
    for i, p in enumerate(r.pages):
        parts.append(f"\n__PAGE_{i + 1}__\n")
        parts.append(p.extract_text() or "")
    text = "\n".join(parts)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n--\s*\d+\s+of\s+\d+\s*--\s*\n", "\n", text, flags=re.I)
    return text


def segment_pagina(segment: str) -> int | None:
    found = PAGE_MARK_RE.findall(segment)
    return int(found[-1]) if found else None


def _image_bytes_white_background(raw: bytes, ext: str) -> tuple[bytes, str]:
    """Si hay transparencia o CMYK, compone sobre blanco (o pasa a RGB) y devuelve bytes + ext."""
    try:
        from PIL import Image
    except ImportError:
        return raw, ext
    ext = ext.lower()
    if ext == "jpeg":
        ext = "jpg"
    try:
        im = Image.open(BytesIO(raw))
    except Exception:
        return raw, ext

    if im.mode == "RGB":
        return raw, ext

    if im.mode == "P" and "transparency" not in im.info:
        return raw, ext

    if im.mode == "P":
        im = im.convert("RGBA")
    elif im.mode == "LA":
        im = im.convert("RGBA")
    elif im.mode == "CMYK":
        im = im.convert("RGB")
        buf = BytesIO()
        if ext == "jpg":
            im.save(buf, format="JPEG", quality=92, optimize=True)
            return buf.getvalue(), "jpg"
        im.save(buf, format="PNG", optimize=True)
        return buf.getvalue(), "png"

    if im.mode == "RGBA":
        white = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(white, im).convert("RGB")
    else:
        im = im.convert("RGB")

    buf = BytesIO()
    if ext == "jpg":
        im.save(buf, format="JPEG", quality=92, optimize=True)
        return buf.getvalue(), "jpg"
    im.save(buf, format="PNG", optimize=True)
    return buf.getvalue(), "png"


def extract_pdf_images_fitz(pdf_path: Path, out_dir: Path, stem_slug: str) -> int:
    """Guarda imágenes incrustadas como {stem}_p{pag:02d}_i{idx:02d}.{ext}. Retorna cantidad."""
    try:
        import fitz
    except ImportError:
        print("Aviso: pymupdf no instalado; sin extracción de imágenes. pip install pymupdf", file=sys.stderr)
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    n_saved = 0
    try:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pagenum = page_idx + 1
            for img_i, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                try:
                    info = doc.extract_image(xref)
                except Exception:
                    continue
                ext = (info.get("ext") or "png").lower()
                if ext == "jpeg":
                    ext = "jpg"
                raw = info.get("image")
                if not raw:
                    continue
                raw, ext = _image_bytes_white_background(raw, ext)
                fname = f"{stem_slug}_p{pagenum:02d}_i{img_i + 1:02d}.{ext}"
                (out_dir / fname).write_bytes(raw)
                n_saved += 1
    finally:
        doc.close()
    return n_saved


def best_image_relpath_for_page(
    pagina: int | None,
    assets_dir: Path,
    stem_slug: str,
) -> str | None:
    """Entre las imágenes de esa página, elige la de mayor tamaño (suele ser la foto de producto)."""
    if pagina is None or not assets_dir.is_dir():
        return None
    prefix = f"{stem_slug}_p{pagina:02d}_"
    candidates = [f for f in assets_dir.iterdir() if f.is_file() and f.name.startswith(prefix)]
    if not candidates:
        return None
    best = max(candidates, key=lambda p: p.stat().st_size)
    try:
        return str(best.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(best).replace("\\", "/")


def imagenes_manifest(assets_dir: Path, stem_slug: str) -> dict[str, list[str]]:
    """pagina str -> lista de rutas relativas al repo."""
    if not assets_dir.is_dir():
        return {}
    by_page: dict[str, list[str]] = {}
    pat = re.compile(rf"^{re.escape(stem_slug)}_p(\d+)_i\d+\.")
    for f in sorted(assets_dir.iterdir()):
        if not f.is_file():
            continue
        m = pat.match(f.name)
        if not m:
            continue
        pnum = m.group(1)
        try:
            rel = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            rel = str(f).replace("\\", "/")
        by_page.setdefault(pnum, []).append(rel)
    return by_page


def parse_cop(num: str) -> int | None:
    # 299.000 o 1.699.000 (separador de miles)
    digits = num.replace(".", "")
    return int(digits) if digits.isdigit() else None


def clean_desc(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_name(lines: list[str]) -> str:
    if not lines:
        return "Producto"
    first = lines[0].strip()
    last = lines[-1].strip()
    # Código / referencia al final (L18, F913B, G105162HST, etc.)
    tail = last
    if re.match(r"^[\w\-+.]{2,40}$", tail) and len(lines) >= 2:
        head = first[:100]
        if head != tail and len(head) > 3:
            return f"{head} — {tail}"[:220]
    if last.lower().startswith("medidas:") and len(lines) >= 2:
        for ln in reversed(lines[:-1]):
            if not ln.lower().startswith("medidas:"):
                return f"{ln} ({last})"[:220]
    if last.upper() in ("IVA INCLUIDO",):
        return lines[-2][:220] if len(lines) >= 2 else "Producto"
    return last[:220]


def extract_products(text: str) -> list[dict]:
    # Precios: $299.000 (lista) o +410.000 / espacio +270.000 (complemento sobre otro ítem).
    price_re = re.compile(
        r"(?:"
        r"\$\s*"
        r"|(?:^|\s)\+\s*"
        r")(\d{1,3}(?:\.\d{3})+)\s*(?:IVA\s+INCLUIDO)?",
        re.I | re.M,
    )
    matches = list(price_re.finditer(text))
    out: list[dict] = []
    junk_name = re.compile(
        r"^(tiempo de respuesta|frecuencia de actualización(\s*\([^)]*\))?|iva incluido|pivot|"
        r"controlador|1ms(\s+ips)?|0[,.]5ms|speakers?|ajustable|"
        r"tecnología:\s*amd freesync|iempo de respuesta)\s*$",
        re.I,
    )

    for i, m in enumerate(matches):
        prev_end = matches[i - 1].end() if i else 0
        segment = text[prev_end : m.start()].strip()
        # Página: último __PAGE__ en todo el texto hasta este precio (no solo el segmento,
        # porque el marcador suele ir una sola vez al inicio de cada página).
        pagina_pdf = segment_pagina(text[: m.start()])
        raw = m.group(0).strip()
        val = parse_cop(m.group(1))
        if val is None or val < 1000:
            continue
        lines = [
            ln.strip()
            for ln in segment.split("\n")
            if ln.strip()
            and not ln.strip().startswith("--")
            and not PAGE_LINE_RE.match(ln.strip())
        ]
        desc = clean_desc(" ".join(lines))
        if len(desc) < 2:
            desc = "Producto según catálogo PDF (precio listado)."
        nombre = build_name(lines)
        if junk_name.match(nombre.strip()):
            for ln in reversed(lines):
                if not junk_name.match(ln.strip()) and len(ln.strip()) > 5:
                    nombre = ln.strip()[:220]
                    break
        # True si en el PDF el precio iba como +95.000 (adicional), no como $95.000
        raw_head = text[m.start() : m.start() + 12].lstrip()
        precio_es_complemento = raw_head.startswith("+")
        out.append(
            {
                "nombre": nombre,
                "imagen": None,
                "descripcion": desc[:3500],
                "precio": val,
                "precio_es_complemento": precio_es_complemento,
                "pagina_pdf": pagina_pdf,
            }
        )
    return out


def looks_like_monitor(nombre: str, desc: str) -> bool:
    """Heurística: ítem de pantalla / monitor del catálogo (excluye torres, portátiles, móviles)."""
    blob = f"{nombre} {desc}".upper()
    blob_norm = blob.replace("´", "'")
    desc_u = desc.upper()

    # Bloques de teclado/raton o escritorio gamer (no es “solo monitor”)
    if "TECLADO Y MOUSE" in desc_u[:400]:
        return False
    if "BASE DE FIBRA" in blob_norm or "PORTAVASOS" in blob_norm:
        return False

    excluir = (
        "CHASIS ",
        "CHASIS GAMER",
        "CAJA ATX",
        "EQUIPO POWER GROUP",
        "POWER GROUP G",
        "LANDER 500",
        "F-937",
        "LANDER",
        "NUC ",
        "GALAXY ",
        "NOTE 60",
        "TABLETS",
        "TAB Z",
        "TAB TB",
        "CELULARES",
        "USB-AC53",
        "ADAPTADOR USB",
        "VIVOBOOK",
        "INSPIRÓN",
        "INSPIRON",
        "LOQ ",
        "THIN A15",
        "GAMING VICTUS",
        "GAMING ACER NITRO",
        "NL16-71G",
        "ANV15-42",
        "15-FA0021LA",
        "15-FB3019LA",
        "M1502-",
        "255 G10B",
        "OPCIONES DE MONITORES PARA COMPRA",  # párrafo introductorio
    )
    if any(x in blob_norm for x in excluir):
        return False
    if "SIN UNIDAD QUEMADORA" in blob_norm and "RTX" in blob_norm:
        return False

    incluir = (
        "MONITOR",
        "MONITORES GAMING",
        "NITRO ",
        "NITRO\"",
        "NITRO”",
        "VG249",
        "VG279",
        "VG27",
        "VG24",
        "KA242",
        "KA272",
        "KG240",
        "KG270",
        "KG272",
        "ED270",
        "ED340",
        "XZ322",
        "XV240",
        "XV270",
        "KGB271",
        "VA259",
        "TUF GAMING",
        "ESCRITORIO GAMER",
        "ULTRAWIDE",
        "ULTRA WIDE",
        "CURVO 31.5",
        "CURVO 34",
        "UM.CE0",
    )
    return any(x in blob_norm for x in incluir)


def filter_monitores_precio_lista(products: list[dict]) -> list[dict]:
    out = []
    for p in products:
        if p.get("precio_es_complemento"):
            continue
        if not looks_like_monitor(p.get("nombre", ""), p.get("descripcion", "")):
            continue
        compra = int(p["precio"])
        row = {
            "nombre": p["nombre"],
            "imagen": p.get("imagen"),
            "descripcion": p["descripcion"],
            "precio_compra": compra,
            "precio_venta": compra + MARGEN_VENTA_SOBRE_COMPRA_COP,
        }
        if p.get("pagina_pdf") is not None:
            row["pagina_pdf"] = p["pagina_pdf"]
        out.append(row)
    return out


def main() -> None:
    raw_argv = sys.argv[1:]
    sin_imagenes = "--sin-imagenes" in raw_argv
    argv = [a for a in raw_argv if a != "--sin-imagenes"]
    if not argv:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    pdf_path = Path(argv[0])
    out_path = Path(argv[1]) if len(argv) > 1 else pdf_path.with_suffix(".productos.json")
    stem_slug = pdf_stem_slug(pdf_path)
    assets_dir = REPO_ROOT / "data" / "pdf_assets" / stem_slug

    if not sin_imagenes:
        n_img = extract_pdf_images_fitz(pdf_path, assets_dir, stem_slug)
        print(f"OK {n_img} imagenes incrustadas -> {assets_dir.relative_to(REPO_ROOT)}")

    text = pdf_to_text(pdf_path)
    products = extract_products(text)
    for p in products:
        p["imagen"] = (
            None
            if sin_imagenes
            else best_image_relpath_for_page(p.get("pagina_pdf"), assets_dir, stem_slug)
        )

    carpeta_rel = (
        None
        if sin_imagenes
        else str(assets_dir.relative_to(REPO_ROOT)).replace("\\", "/")
    )
    payload = {
        "fuente": pdf_path.name,
        "total": len(products),
        "carpeta_imagenes_pdf": carpeta_rel,
        "nota_imagenes": (
            "imagen: ruta relativa al repo hacia la extracción PyMuPDF; se elige la imagen más pesada "
            "de la misma pagina_pdf que el texto del producto (varios productos en una página pueden "
            "compartir la misma foto: revisar manualmente). Las imágenes con transparencia se guardan "
            "compuestas sobre fondo blanco (Pillow). Sin --sin-imagenes se vuelcan todas las imágenes "
            "en carpeta_imagenes_pdf; ver imagenes_por_pagina."
            if not sin_imagenes
            else "Extracción de imágenes omitida (--sin-imagenes)."
        ),
        "advertencia": (
            "Extracción automática: hay precios tipo +270.000 (complemento de otro ítem) y leyendas "
            "promocionales (ej. ANTES:/AHORA:). Revisa y unifica nombres manualmente donde haga falta."
        ),
        "moneda": "COP",
        "imagenes_por_pagina": {}
        if sin_imagenes
        else imagenes_manifest(assets_dir, stem_slug),
        "productos": products,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {len(products)} productos -> {out_path}")

    mon_path = out_path.with_name(
        out_path.stem.replace(".productos", "") + "_monitores_precio_lista.json"
    )
    if mon_path == out_path:
        mon_path = out_path.parent / "lista_monitores_precio_lista.json"
    mons = filter_monitores_precio_lista(products)
    mon_payload = {
        "fuente": pdf_path.name,
        "criterio": "Monitores (heurística) con precio en PDF como $…, no como +… (complemento).",
        "total": len(mons),
        "moneda": "COP",
        "margen_venta_sobre_compra_cop": MARGEN_VENTA_SOBRE_COMPRA_COP,
        "nota_precios": (
            "precio_compra: valor según lista PDF. "
            "precio_venta: precio_compra + margen_venta_sobre_compra_cop."
        ),
        "carpeta_imagenes_pdf": carpeta_rel,
        "nota_imagenes": payload["nota_imagenes"],
        "imagenes_por_pagina": payload["imagenes_por_pagina"],
        "productos": mons,
    }
    mon_path.write_text(json.dumps(mon_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {len(mons)} monitores precio lista -> {mon_path}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--solo-imagenes":
        if len(args) < 2:
            print("Uso: python scripts/extract_lista_pdf.py --solo-imagenes lista.pdf", file=sys.stderr)
            sys.exit(1)
        pdf_path = Path(args[1])
        stem = pdf_stem_slug(pdf_path)
        d = REPO_ROOT / "data" / "pdf_assets" / stem
        n = extract_pdf_images_fitz(pdf_path, d, stem)
        print(f"OK {n} imagenes -> {d.relative_to(REPO_ROOT)}")
        print(json.dumps(imagenes_manifest(d, stem), ensure_ascii=False, indent=2))
        sys.exit(0)
    main()
