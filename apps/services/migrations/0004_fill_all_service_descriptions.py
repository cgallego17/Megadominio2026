from django.db import migrations


def fill_all_service_descriptions(apps, schema_editor):
    Service = apps.get_model('services', 'Service')

    def build_description(name: str) -> str:
        n = (name or '').lower()
        blocks = []

        def add_common_intro(title: str):
            blocks.append(
                f"{title} con enfoque comercial y técnico, diseñado para maximizar conversión, rendimiento y posicionamiento SEO."
            )

        def add_benefits(items):
            blocks.append(
                "Beneficios comerciales: " + "; ".join(items) + "."
            )

        def add_tech(items):
            blocks.append(
                "Implementación técnica: " + "; ".join(items) + "."
            )

        def add_seo(items):
            blocks.append(
                "SEO/Medición: " + "; ".join(items) + "."
            )

        # Categorías por palabras clave
        if any(k in n for k in ["landing", "sitio", "portal", "web", "e-commerce", "ecommerce"]):
            add_common_intro("Desarrollo Web profesional")
            add_benefits([
                "presencia digital sólida",
                "mejor tasa de conversión",
                "experiencia de usuario optimizada",
                "escala y mantenibilidad"
            ])
            add_tech([
                "arquitectura limpia (Django/DRF/Next.js según caso)",
                "Core Web Vitals (LCP, CLS, INP) 90+",
                "seguridad (HTTPS, CSP, HSTS), autenticación y permisos",
                "CI/CD, contenedores, CDN y cacheo avanzado"
            ])
            add_seo([
                "estructura semántica H1–H3",
                "metaetiquetas y Open Graph",
                "Schema.org (Breadcrumb, WebSite)",
                "Search Console y analítica de eventos"
            ])
        elif any(k in n for k in ["marketing", "ads", "campaña", "sem", "smm"]):
            add_common_intro("Marketing Digital 360° y performance ads")
            add_benefits([
                "crecimiento de ventas con ROAS/CPA controlado",
                "audiencias precisas y remarketing",
                "mensajes y creatividades que convierten"
            ])
            add_tech([
                "tagging con GTM y Conversion API",
                "eventos server-side y DataLayer estandarizado",
                "dashboards en tiempo real y atribución multi-touch"
            ])
            add_seo([
                "research de keywords transaccionales",
                "landing pages relevantes y de alta calidad",
                "testing A/B y mejora continua"
            ])
        elif "seo" in n or "posicion" in n:
            add_common_intro("SEO técnico + contenido + autoridad")
            add_benefits([
                "tráfico orgánico cualificado",
                "menor dependencia de pauta",
                "visibilidad sostenible en buscadores"
            ])
            add_tech([
                "auditoría técnica (indexación, CWV, logs)",
                "datos estructurados (FAQ, Article, Product)",
                "arquitectura de enlaces e interlinking",
                "hreflang, canónicos y limpieza de errores 3xx/4xx/5xx"
            ])
            add_seo([
                "E-E-A-T y plan editorial por clusters",
                "optimización de snippets y rich results",
                "monitoring con Search Console y analytics"
            ])
        elif any(k in n for k in ["branding", "logo", "identidad", "diseño", "grafico", "gráfico"]):
            add_common_intro("Branding y diseño gráfico orientado a resultados")
            add_benefits([
                "diferenciación competitiva",
                "consistencia visual cross-channel",
                "mejor recordación de marca"
            ])
            add_tech([
                "manual de marca y sistema de componentes",
                "archivos escalables (SVG/AI/WEBP) optimizados",
                "guías para web, social y print"
            ])
            add_seo([
                "nombres/alt/title optimizados",
                "accesibilidad AA",
                "velocidad de carga con recursos modernos"
            ])
        elif any(k in n for k in ["automat", "rpa", "workflow", "zapier", "make", "api"]):
            add_common_intro("Automatización de procesos e integraciones")
            add_benefits([
                "reducción de costos operativos",
                "menos errores manuales",
                "escalabilidad y continuidad de negocio"
            ])
            add_tech([
                "integraciones API/OAuth2 y webhooks",
                "colas de mensajes y reintentos idempotentes",
                "observabilidad (logs, métricas, trazas)"
            ])
            add_seo([
                "mejora de tiempos en journeys críticos",
                "impacto positivo en conversión y UX"
            ])
        elif any(k in n for k in ["consultor", "estrateg", "roadmap", "auditor"]):
            add_common_intro("Consultoría digital y estrategia tecnológica")
            add_benefits([
                "priorización por impacto/efuerzo",
                "alineación de stakeholders",
                "reducción de riesgo y time-to-value"
            ])
            add_tech([
                "diagnóstico de capacidades y arquitectura de referencia",
                "backlog priorizado y plan de medición con OKRs",
                "gobernanza y estándares de calidad"
            ])
            add_seo([
                "alineación de contenidos con intención de búsqueda",
                "auditorías on/off-page",
                "hoja de ruta para crecimiento orgánico"
            ])
        elif any(k in n for k in ["hosting", "servidor", "vps", "cloud"]):
            add_common_intro("Hosting administrado y alto rendimiento")
            add_benefits([
                "estabilidad y uptime",
                "baja latencia",
                "soporte experto"
            ])
            add_tech([
                "monitoring, backups y CDN",
                "hardening y WAF",
                "autoscaling y cachés de aplicación"
            ])
            add_seo([
                "mejores tiempos de carga",
                "mejor experiencia de usuario y ranking"
            ])
        elif any(k in n for k in ["dominio", "dns"]):
            add_common_intro("Gestión de dominios y DNS segura")
            add_benefits([
                "configuraciones correctas y seguras",
                "renovaciones a tiempo",
                "conectividad estable"
            ])
            add_tech([
                "DNSSEC, registros SPF/DKIM/DMARC",
                "automatización de renovaciones",
                "monitoring de salud de zona"
            ])
            add_seo([
                "evita caídas por DNS",
                "mejora de entregabilidad y reputación"
            ])
        elif any(k in n for k in ["manten", "soporte", "sop"]):
            add_common_intro("Mantenimiento y soporte proactivo")
            add_benefits([
                "continuidad operativa",
                "prevención de incidentes",
                "optimización continua"
            ])
            add_tech([
                "actualizaciones, parches y monitoreo",
                "SLA definido y mesa de ayuda",
                "observabilidad de errores y performance"
            ])
            add_seo([
                "sitio saludable y rápido",
                "mejor experiencia y retención"
            ])
        elif any(k in n for k in ["correo", "email", "workspace", "office"]):
            add_common_intro("Email y productividad en la nube")
            add_benefits([
                "colaboración eficiente",
                "seguridad y cumplimiento",
                "menor carga de TI"
            ])
            add_tech([
                "provisionamiento, políticas y backups",
                "SSO/MFA y DLP",
                "migraciones sin interrupciones"
            ])
            add_seo([
                "mejor entregabilidad (SPF/DKIM/DMARC)",
                "reputación de dominio estable"
            ])
        elif any(k in n for k in ["ssl", "cert", "segur", "waf", "backup", "respaldo", "antivirus", "firewall"]):
            add_common_intro("Seguridad y continuidad del negocio")
            add_benefits([
                "protección de datos",
                "confianza del usuario",
                "menor exposición a incidentes"
            ])
            add_tech([
                "certificados SSL/TLS, WAF y hardening",
                "copias de seguridad y restauración",
                "monitoreo y respuesta a incidentes"
            ])
            add_seo([
                "sitio seguro (HTTPS) como señal de ranking",
                "reducción de rebote por confianza del usuario"
            ])
        elif any(k in n for k in ["optimiz", "velocidad", "cache", "caché", "caching"]):
            add_common_intro("Optimización de rendimiento web")
            add_benefits([
                "mejor conversión",
                "mejor experiencia del usuario",
                "menor consumo de recursos"
            ])
            add_tech([
                "optimización de assets, imágenes y fuentes",
                "cachés (HTTP, aplicación) y CDN",
                "tuning de base de datos y server"
            ])
            add_seo([
                "CWV y tiempos de carga rápidos",
                "mejor ranking y crawl budget"
            ])
        elif any(k in n for k in ["migraci", "traslado", "move"]):
            add_common_intro("Migración de sitios y sistemas")
            add_benefits([
                "cero o mínima indisponibilidad",
                "riesgo controlado",
                "mejor plataforma final"
            ])
            add_tech([
                "plan de rollback, verificación y pruebas",
                "sincronización de datos y DNS cutover",
                "monitoreo post-migración"
            ])
            add_seo([
                "preserva posicionamiento (redirecciones/URLs)",
                "evita pérdida de tráfico"
            ])
        elif any(k in n for k in ["redes sociales", "facebook", "instagram", "social"]):
            add_common_intro("Gestión de redes sociales y contenido")
            add_benefits([
                "crecimiento de comunidad",
                "engagement y awareness",
                "alineación con objetivos de negocio"
            ])
            add_tech([
                "calendario editorial, guidelines y creatividades",
                "automatización de publicaciones y social listening",
                "reportes con KPIs accionables"
            ])
            add_seo([
                "mejor distribución y señal social",
                "tráfico de referencia de calidad"
            ])
        else:
            add_common_intro(name or "Servicio Digital")
            add_benefits([
                "mejora de resultados de negocio",
                "experiencia de usuario superior",
                "medición y mejora continua"
            ])
            add_tech([
                "buenas prácticas de seguridad y performance",
                "documentación y soporte",
                "despliegue estable y monitoreado"
            ])
            add_seo([
                "optimización técnica y de contenidos",
                "seguimiento constante con analítica"
            ])

        return "\n\n".join(blocks)

    for svc in Service.objects.all():
        text = build_description(svc.name)
        if not svc.description or len((svc.description or '').strip()) < 200:
            svc.description = text
            svc.save(update_fields=['description'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_update_long_descriptions'),
    ]

    operations = [
        migrations.RunPython(fill_all_service_descriptions, noop),
    ]
