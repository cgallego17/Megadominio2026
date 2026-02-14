from django.db import migrations


def update_long_descriptions(apps, schema_editor):
    Service = apps.get_model('services', 'Service')

    payload = {
        'Desarrollo Web': {
            'description': (
                "Servicio integral de diseño y desarrollo web orientado a conversión y rendimiento. "
                "Incluye arquitectura de la información, UI/UX responsive, implementación con Django/Next.js, "
                "optimizaciones Core Web Vitals (LCP, CLS, INP), SEO técnico on-page, seguridad (HTTPS, CSP, HSTS), "
                "y despliegue en infraestructura escalable (Docker, CI/CD).\n\n"
                "Beneficios comerciales: presencia digital profesional, incremento de leads, mayor velocidad de carga, "
                "y analítica accionable con eventos personalizados.\n\n"
                "Entregables técnicos: código versionado, documentación de endpoints/infra, mapas de sitio XML/HTML, "
                "microdatos/Schema.org, integración con CDN, cacheo, y pruebas E2E.\n\n"
                "SEO: palabras clave objetivo (desarrollo web corporativo, sitios web profesionales, páginas de aterrizaje), "
                "meta etiquetas optimizadas, estructura H1–H3 semántica, y performance 90+ en Lighthouse."
            )
        },
        'Marketing Digital': {
            'description': (
                "Estrategias 360° en Google Ads, Meta Ads y remarketing orientadas a ROAS. "
                "Incluye investigación de palabras clave, creación de audiencias (lookalike/retargeting), "
                "creatividades A/B, funnels, y dashboards en tiempo real.\n\n"
                "Beneficios comerciales: crecimiento sostenido en ventas, reducción de CPA, mayor tasa de conversión.\n\n"
                "Implementación técnica: tagging con GTM, Conversion API, eventos server-side, "
                "DataLayer estandarizado, UTMs consistentes, y atribución multi-touch.\n\n"
                "SEO/SEM: keywords transaccionales, anuncios responsivos, extensiones, landing pages con alta relevancia, "
                "y calidad de anuncio optimizada para bajar CPC."
            )
        },
        'SEO / Posicionamiento': {
            'description': (
                "SEO técnico + contenido + autoridad. Auditoría de indexación, rendimiento, arquitectura de enlaces, "
                "y datos estructurados. Plan editorial basado en intención de búsqueda y clusters temáticos.\n\n"
                "Beneficios comerciales: tráfico orgánico cualificado, posicionamiento sostenible y reducción de inversión paga.\n\n"
                "Implementación técnica: sitemap y robots, Core Web Vitals, schema (Product, FAQ, Breadcrumb), "
                "optimización de interlinking, canónicos, hreflang, y corrección de errores 3xx/4xx/5xx.\n\n"
                "SEO: keyword research, E-E-A-T, optimización de snippets, y seguimiento con Search Console."
            )
        },
        'Diseño Gráfico / Branding': {
            'description': (
                "Construcción y evolución de marca: identidad visual, manual de marca, sistemas de componentes, "
                "y creatividades para campañas. Diseño centrado en objetivos de negocio y consistencia cross-channel.\n\n"
                "Beneficios comerciales: diferenciación competitiva, recordación de marca y coherencia visual.\n\n"
                "Entregables técnicos: logotipos en formatos escalables, paletas/ tipografías, grids, "
                "y librerías para web/social/impresos con guías de uso.\n\n"
                "SEO/Brand: activos optimizados (nombres/alt/title), accesibilidad AA, y preparación para WebP/SVG."
            )
        },
        'Automatización de Procesos': {
            'description': (
                "Orquestación y automatización con APIs, webhooks y RPA para eliminar tareas repetitivas. "
                "Integraciones con CRM/ERP, Zapier/Make, y pipelines serverless.\n\n"
                "Beneficios comerciales: reducción de costos operativos, menor error humano y escalabilidad.\n\n"
                "Implementación técnica: autenticación OAuth2/API Keys, colas de mensajes, reintentos idempotentes, "
                "observabilidad (logs, trazas), y pruebas contractuales.\n\n"
                "SEO/Impacto: mejora de tiempos de respuesta en flujos críticos que impactan experiencia y conversión."
            )
        },
        'Consultoría Digital': {
            'description': (
                "Acompañamiento estratégico para transformación digital: diagnóstico, roadmap, KPIs, "
                "y gobernanza tecnológica. Talleres con stakeholders y priorización por impacto/esfuerzo.\n\n"
                "Beneficios comerciales: foco en iniciativas con ROI, reducción de riesgo y alineación organizacional.\n\n"
                "Entregables técnicos: matriz de capacidades, backlog priorizado, arquitectura de referencia, "
                "y plan de medición con OKRs.\n\n"
                "SEO/Estrategia: alineación de contenidos con intención de búsqueda, auditorías on/off-page "
                "y plan de crecimiento orgánico."
            )
        },
    }

    for name, data in payload.items():
        try:
            svc = Service.objects.filter(name=name).first()
            if svc:
                svc.description = data['description']
                svc.save(update_fields=['description'])
        except Exception:
            # Silencioso: si no existe el servicio aún, se ignora
            pass


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_seed_top_services'),
    ]

    operations = [
        migrations.RunPython(update_long_descriptions, noop),
    ]
