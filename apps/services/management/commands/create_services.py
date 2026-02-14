from django.core.management.base import BaseCommand
from apps.services.models import Service


class Command(BaseCommand):
    help = 'Crea los servicios iniciales en la base de datos'

    def handle(self, *args, **kwargs):
        services = [
            # Desarrollo Web
            {
                'name': 'Landing Page',
                'description': 'Página de aterrizaje profesional optimizada para conversión de visitantes en clientes. Diseño moderno y responsive que destaca tu propuesta de valor.',
                'price': 2100000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Sitio Web Corporativo',
                'description': 'Sitio web institucional completo con 5-10 páginas. Incluye diseño profesional, formularios de contacto, integración con redes sociales y optimización SEO básica.',
                'price': 6300000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Portal Web Avanzado',
                'description': 'Sitio web complejo con funcionalidades personalizadas, panel de administración, gestión de usuarios y características avanzadas según tus necesidades específicas.',
                'price': 14700000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'E-commerce Básico',
                'description': 'Tienda online profesional hasta 50 productos. Incluye carrito de compras, pasarela de pagos, gestión de inventario y panel administrativo completo.',
                'price': 8400000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'E-commerce Profesional',
                'description': 'Tienda online empresarial con productos ilimitados, múltiples métodos de pago, sistema de envíos, reportes avanzados y funcionalidades premium.',
                'price': 18900000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Sistema a Medida',
                'description': 'Desarrollo de software personalizado según tus necesidades. CRM, ERP, sistemas de gestión o cualquier aplicación web específica para tu negocio.',
                'price': 21000000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Blog / Portal de Noticias',
                'description': 'Sitio web con gestor de contenidos optimizado para blogs o portales de noticias. Incluye categorías, etiquetas, comentarios y área de administración intuitiva.',
                'price': 5000000.00,
                'billing_type': 'unique',
            },
            
            # Hosting y Dominios
            {
                'name': 'Hosting Básico',
                'description': '5GB de espacio en disco, 1 dominio incluido, certificado SSL gratis, panel de control cPanel y soporte técnico. Ideal para sitios web pequeños.',
                'price': 42000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Hosting Profesional',
                'description': '20GB de espacio, hasta 3 dominios, SSL premium, CDN para velocidad, backups semanales y soporte prioritario. Perfecto para empresas.',
                'price': 105000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Hosting Premium',
                'description': '50GB de espacio, dominios ilimitados, SSL premium, CDN global, backups diarios automáticos, soporte 24/7 y recursos garantizados.',
                'price': 210000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Servidor VPS',
                'description': 'Servidor virtual privado dedicado con recursos exclusivos. Control total, mayor rendimiento y escalabilidad para proyectos exigentes.',
                'price': 336000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Registro de Dominio',
                'description': 'Registro y gestión de tu nombre de dominio (.com, .net, .org, etc). Incluye gestión DNS, privacidad WHOIS y renovación automática.',
                'price': 126000.00,
                'billing_type': 'annual',
            },
            
            # Marketing Digital
            {
                'name': 'Gestión de Redes Sociales',
                'description': 'Administración profesional de hasta 3 redes sociales. Incluye creación de contenido, publicaciones programadas, interacción con seguidores y reportes mensuales.',
                'price': 1260000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Publicidad en Google Ads',
                'description': 'Creación y gestión de campañas publicitarias en Google. Investigación de palabras clave, optimización continua y reportes detallados de rendimiento.',
                'price': 1680000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Publicidad en Facebook/Instagram',
                'description': 'Campañas publicitarias en redes sociales Meta. Segmentación avanzada, creatividades atractivas y análisis de resultados para maximizar conversiones.',
                'price': 1470000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'SEO Básico',
                'description': 'Optimización inicial para motores de búsqueda. Incluye auditoría SEO, optimización on-page, mejora de velocidad y reportes mensuales de posicionamiento.',
                'price': 1050000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'SEO Avanzado',
                'description': 'Estrategia completa de posicionamiento orgánico. Incluye link building, contenido optimizado, SEO técnico avanzado y análisis competitivo.',
                'price': 2520000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Email Marketing',
                'description': 'Campañas de correo electrónico automatizadas. Diseño de newsletters, segmentación de audiencia, automatización de envíos y análisis de métricas.',
                'price': 840000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Estrategia Digital Integral',
                'description': 'Plan completo de marketing digital personalizado. Incluye SEO, redes sociales, publicidad pagada, email marketing y análisis de resultados.',
                'price': 4200000.00,
                'billing_type': 'monthly',
            },
            
            # Diseño
            {
                'name': 'Diseño de Logo',
                'description': 'Logo profesional único para tu marca. Incluye 3 propuestas iniciales, revisiones ilimitadas y entrega en todos los formatos necesarios.',
                'price': 1050000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Identidad Corporativa',
                'description': 'Identidad visual completa para tu empresa. Incluye logo, manual de marca, paleta de colores, tipografías, papelería y aplicaciones.',
                'price': 2520000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Diseño de Banner Publicitario',
                'description': 'Set de banners publicitarios para web y redes sociales. Diseños atractivos optimizados para diferentes formatos y plataformas.',
                'price': 420000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Diseño de Material Gráfico',
                'description': 'Diseño de flyers, brochures, catálogos y material impreso. Creatividad profesional lista para impresión o uso digital.',
                'price': 630000.00,
                'billing_type': 'unique',
            },
            
            # Mantenimiento y Soporte
            {
                'name': 'Mantenimiento Web Básico',
                'description': 'Actualizaciones mensuales de seguridad, backup semanal, monitoreo de uptime y corrección de errores menores. Tranquilidad para tu sitio web.',
                'price': 252000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Mantenimiento Web Premium',
                'description': 'Servicio completo de mantenimiento con actualizaciones semanales, backup diario, soporte técnico 24/7, optimización mensual y reportes detallados.',
                'price': 630000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Soporte Técnico por Horas',
                'description': 'Paquete de 5 horas de soporte técnico especializado. Ideal para correcciones, modificaciones pequeñas o asesoría técnica puntual.',
                'price': 840000.00,
                'billing_type': 'unique',
            },
            
            # Email y Comunicación
            {
                'name': 'Email Corporativo Básico',
                'description': '5 cuentas de correo profesionales con tu dominio. Incluye 10GB por cuenta, webmail, protección antispam y sincronización móvil.',
                'price': 63000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Email Corporativo Empresarial',
                'description': '20 cuentas de correo con 50GB cada una. Incluye calendario compartido, contactos sincronizados y herramientas de colaboración.',
                'price': 168000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Google Workspace',
                'description': 'Suite completa de Google para empresas. Email profesional + Drive + Meet + Documentos + Calendar y todas las aplicaciones de Google.',
                'price': 252000.00,
                'billing_type': 'monthly',
            },
            
            # Seguridad
            {
                'name': 'Certificado SSL Premium',
                'description': 'Certificado SSL de validación extendida con barra verde. Máxima confianza y seguridad para tu sitio web y clientes.',
                'price': 840000.00,
                'billing_type': 'annual',
            },
            {
                'name': 'Seguridad Web Avanzada',
                'description': 'Protección completa contra amenazas. Incluye firewall WAF, protección DDoS, escaneo de malware y monitoreo 24/7 de seguridad.',
                'price': 336000.00,
                'billing_type': 'monthly',
            },
            {
                'name': 'Backup Automático',
                'description': 'Sistema de respaldos diarios automáticos con retención de 30 días. Restauración rápida y almacenamiento en la nube seguro.',
                'price': 126000.00,
                'billing_type': 'monthly',
            },
            
            # Optimización
            {
                'name': 'Optimización de Velocidad',
                'description': 'Mejora del rendimiento y velocidad de carga de tu sitio web. Optimización de imágenes, código, base de datos y configuración del servidor.',
                'price': 1680000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Migración de Sitio Web',
                'description': 'Migración completa y segura de tu sitio web a nuevo hosting. Sin tiempo de inactividad, con verificación exhaustiva de funcionamiento.',
                'price': 1260000.00,
                'billing_type': 'unique',
            },
            {
                'name': 'Auditoría Web Completa',
                'description': 'Análisis exhaustivo de tu sitio web. Incluye auditoría SEO, velocidad, seguridad, usabilidad y recomendaciones detalladas de mejora.',
                'price': 1050000.00,
                'billing_type': 'unique',
            },
        ]

        created_count = 0
        updated_count = 0

        for service_data in services:
            service, created = Service.objects.update_or_create(
                name=service_data['name'],
                defaults={
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'billing_type': service_data['billing_type'],
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[+] Creado: {service.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'[*] Actualizado: {service.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nProceso completado!'
                f'\n- Servicios creados: {created_count}'
                f'\n- Servicios actualizados: {updated_count}'
                f'\n- Total: {created_count + updated_count}'
            )
        )
