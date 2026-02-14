from django.db import migrations


def update_complete_descriptions(apps, schema_editor):
    Service = apps.get_model('services', 'Service')

    descriptions = {
        'Desarrollo Web': (
            "En Megadominio transformamos tu visión digital en una experiencia web de alto impacto. "
            "Nuestro servicio de Desarrollo Web abarca desde la conceptualización estratégica hasta "
            "el despliegue en producción, creando sitios corporativos, landing pages de conversión, "
            "plataformas e-commerce y aplicaciones web a medida que no solo se ven increíbles, sino "
            "que generan resultados medibles para tu negocio.\n\n"

            "¿POR QUÉ ELEGIR NUESTRO DESARROLLO WEB?\n\n"

            "Cada proyecto comienza con un análisis profundo de tu mercado, competencia y objetivos "
            "comerciales. No construimos sitios genéricos: diseñamos experiencias digitales que "
            "reflejan la identidad de tu marca y están optimizadas para convertir visitantes en "
            "clientes. Nuestro equipo combina diseño UI/UX centrado en el usuario con ingeniería "
            "de software robusta para entregar productos que escalan con tu empresa.\n\n"

            "BENEFICIOS PARA TU NEGOCIO:\n\n"

            "• Presencia digital profesional que genera confianza desde el primer contacto.\n"
            "• Incremento comprobado en la tasa de conversión gracias a diseño orientado a CTA.\n"
            "• Velocidad de carga optimizada que reduce la tasa de rebote hasta un 40%.\n"
            "• Diseño 100% responsive que garantiza experiencia perfecta en móvil, tablet y desktop.\n"
            "• Arquitectura escalable que crece con tu negocio sin necesidad de reconstruir.\n"
            "• Integración nativa con herramientas de analítica, CRM y pasarelas de pago.\n"
            "• Panel de administración intuitivo para gestionar contenidos sin conocimientos técnicos.\n\n"

            "QUÉ INCLUYE NUESTRO SERVICIO:\n\n"

            "• Análisis de requerimientos y benchmarking competitivo.\n"
            "• Arquitectura de información y wireframes interactivos.\n"
            "• Diseño UI/UX personalizado con prototipos en Figma.\n"
            "• Desarrollo frontend con HTML5, CSS3, JavaScript moderno y frameworks como React o Tailwind CSS.\n"
            "• Desarrollo backend con Django, Django REST Framework y PostgreSQL.\n"
            "• Integración de pasarelas de pago (PayU, MercadoPago, Stripe).\n"
            "• Sistema de gestión de contenidos (CMS) personalizado.\n"
            "• Formularios de contacto, cotización y suscripción.\n"
            "• Chat en vivo y widgets de WhatsApp Business.\n"
            "• Configuración de Google Analytics 4, Google Tag Manager y eventos de conversión.\n"
            "• Optimización de imágenes (WebP/AVIF), lazy loading y compresión de assets.\n"
            "• Certificado SSL/TLS, headers de seguridad (CSP, HSTS, X-Frame-Options).\n"
            "• Sitemap XML, robots.txt y datos estructurados Schema.org.\n\n"

            "PROCESO DE TRABAJO:\n\n"

            "1. Descubrimiento: Reunión inicial para entender tu negocio, audiencia objetivo, "
            "competidores y KPIs. Definimos el alcance, cronograma y entregables.\n"
            "2. Diseño: Creamos wireframes y prototipos interactivos. Iteramos contigo hasta "
            "lograr el diseño perfecto que represente tu marca.\n"
            "3. Desarrollo: Implementamos el frontend y backend con código limpio, versionado "
            "en Git, con pruebas unitarias y de integración.\n"
            "4. QA y Optimización: Realizamos pruebas de rendimiento (Lighthouse 90+), "
            "compatibilidad cross-browser, accesibilidad WCAG 2.1 y seguridad.\n"
            "5. Lanzamiento: Desplegamos en infraestructura de producción con CI/CD, "
            "configuramos CDN, monitoreo y backups automáticos.\n"
            "6. Soporte post-lanzamiento: 30 días de soporte incluido para ajustes, "
            "capacitación del equipo y resolución de incidencias.\n\n"

            "STACK TECNOLÓGICO:\n\n"

            "• Frontend: HTML5, CSS3, Tailwind CSS, JavaScript ES6+, React/Next.js.\n"
            "• Backend: Python, Django 4.x, Django REST Framework, Celery.\n"
            "• Base de datos: PostgreSQL, Redis para caché y colas.\n"
            "• Infraestructura: Docker, Nginx, Gunicorn, CI/CD con GitHub Actions.\n"
            "• CDN y hosting: Cloudflare, AWS/DigitalOcean.\n"
            "• Herramientas: Git, Figma, Jira/Trello, Sentry para monitoreo de errores.\n\n"

            "OPTIMIZACIÓN SEO INCLUIDA:\n\n"

            "Cada sitio web que desarrollamos viene con SEO técnico integrado desde el código: "
            "estructura semántica H1-H6, meta títulos y descripciones únicos por página, "
            "URLs amigables, datos estructurados JSON-LD (Organization, WebSite, BreadcrumbList, "
            "FAQPage), Open Graph y Twitter Cards para redes sociales, canonical tags, "
            "sitemap XML dinámico, robots.txt optimizado, y Core Web Vitals (LCP < 2.5s, "
            "CLS < 0.1, INP < 200ms) para máximo rendimiento en Google.\n\n"

            "Palabras clave: desarrollo web Colombia, diseño de páginas web, crear sitio web "
            "corporativo, desarrollo web profesional, agencia de desarrollo web, landing page "
            "de conversión, tienda virtual, e-commerce Colombia."
        ),

        'Marketing Digital': (
            "Impulsa el crecimiento de tu negocio con estrategias de Marketing Digital basadas "
            "en datos y orientadas a resultados. En Megadominio no solo gestionamos campañas "
            "publicitarias: diseñamos ecosistemas de adquisición completos que atraen, convierten "
            "y fidelizan clientes a través de múltiples canales digitales.\n\n"

            "¿POR QUÉ NECESITAS MARKETING DIGITAL PROFESIONAL?\n\n"

            "El 93% de las experiencias online comienzan en un buscador y el 76% de los consumidores "
            "investigan en línea antes de comprar. Sin una estrategia digital sólida, estás perdiendo "
            "clientes potenciales cada día. Nuestro equipo de especialistas certificados en Google Ads "
            "y Meta Ads diseña campañas que maximizan tu retorno de inversión publicitaria (ROAS) "
            "mientras construyen reconocimiento de marca a largo plazo.\n\n"

            "BENEFICIOS PARA TU NEGOCIO:\n\n"

            "• Incremento medible en ventas y leads cualificados desde el primer mes.\n"
            "• Reducción progresiva del costo por adquisición (CPA) mediante optimización continua.\n"
            "• Audiencias hipersegmentadas que llegan al cliente ideal en el momento preciso.\n"
            "• Remarketing inteligente que recupera hasta un 26% de carritos abandonados.\n"
            "• Dashboards en tiempo real para tomar decisiones basadas en datos.\n"
            "• Presencia omnicanal: Google, Facebook, Instagram, LinkedIn, YouTube y TikTok.\n"
            "• Escalabilidad controlada: aumentamos inversión solo cuando los números lo respaldan.\n\n"

            "QUÉ INCLUYE NUESTRO SERVICIO:\n\n"

            "• Auditoría completa de presencia digital actual y análisis competitivo.\n"
            "• Definición de buyer personas y customer journey mapping.\n"
            "• Estrategia de campañas multicanal con presupuesto optimizado.\n"
            "• Investigación de palabras clave transaccionales e informacionales.\n"
            "• Creación de campañas en Google Ads (Search, Display, Shopping, YouTube, Performance Max).\n"
            "• Creación de campañas en Meta Ads (Facebook e Instagram) con audiencias lookalike.\n"
            "• Diseño de creatividades publicitarias (imágenes, carruseles, videos cortos).\n"
            "• Landing pages de conversión optimizadas para cada campaña.\n"
            "• Configuración de píxeles, Conversion API y eventos server-side.\n"
            "• Testing A/B de anuncios, audiencias y landing pages.\n"
            "• Implementación de funnels de venta y automatización de email marketing.\n"
            "• Reportes semanales y mensuales con métricas clave (ROAS, CPA, CTR, CVR).\n"
            "• Reuniones de revisión estratégica quincenal.\n\n"

            "PROCESO DE TRABAJO:\n\n"

            "1. Diagnóstico: Analizamos tu situación actual, competencia, mercado y objetivos "
            "de negocio. Definimos KPIs y presupuesto óptimo.\n"
            "2. Estrategia: Diseñamos el plan de medios, seleccionamos canales, definimos "
            "audiencias y creamos el calendario de campañas.\n"
            "3. Implementación: Configuramos tracking avanzado (GTM, GA4, Conversion API), "
            "creamos campañas, anuncios y landing pages.\n"
            "4. Optimización: Monitoreamos diariamente, ajustamos pujas, pausamos anuncios "
            "de bajo rendimiento y escalamos los ganadores.\n"
            "5. Reporting: Entregamos informes claros con insights accionables y "
            "recomendaciones para el siguiente período.\n\n"

            "STACK Y HERRAMIENTAS:\n\n"

            "• Plataformas: Google Ads, Meta Business Suite, LinkedIn Ads, TikTok Ads.\n"
            "• Tracking: Google Tag Manager, Google Analytics 4, Meta Pixel, Conversion API.\n"
            "• Automatización: Mailchimp, ActiveCampaign, HubSpot.\n"
            "• Creatividades: Canva Pro, Adobe Creative Suite, CapCut.\n"
            "• Reporting: Google Data Studio (Looker Studio), dashboards personalizados.\n"
            "• CRO: Hotjar, Microsoft Clarity para mapas de calor y grabaciones.\n\n"

            "OPTIMIZACIÓN SEO/SEM:\n\n"

            "Nuestras campañas están respaldadas por investigación SEO profunda: identificamos "
            "las keywords con mayor intención de compra, optimizamos Quality Score para reducir "
            "CPC, creamos landing pages con relevancia máxima, y alineamos la estrategia de "
            "contenido orgánico con la pauta para maximizar la cobertura en resultados de búsqueda.\n\n"

            "Palabras clave: marketing digital Colombia, agencia de publicidad digital, "
            "campañas Google Ads, publicidad en Facebook, gestión de redes sociales, "
            "marketing de performance, agencia SEM Colombia, publicidad digital Bogotá."
        ),

        'SEO / Posicionamiento': (
            "Posiciona tu negocio en los primeros resultados de Google de forma orgánica y "
            "sostenible. Nuestro servicio de SEO combina auditoría técnica avanzada, estrategia "
            "de contenidos basada en intención de búsqueda y construcción de autoridad para "
            "generar tráfico cualificado que se convierte en clientes reales.\n\n"

            "¿POR QUÉ INVERTIR EN SEO?\n\n"

            "El 68% de todas las experiencias online comienzan con una búsqueda en Google. "
            "Los primeros 3 resultados orgánicos capturan el 75% de los clics. A diferencia "
            "de la publicidad paga, el SEO genera tráfico compuesto: cada mejora se acumula "
            "mes a mes, reduciendo tu dependencia de pauta y construyendo un activo digital "
            "que trabaja para tu negocio 24/7.\n\n"

            "BENEFICIOS PARA TU NEGOCIO:\n\n"

            "• Tráfico orgánico cualificado con alta intención de compra.\n"
            "• Reducción progresiva del costo de adquisición de clientes.\n"
            "• Visibilidad sostenible que no desaparece al pausar la inversión.\n"
            "• Mayor credibilidad y confianza: los usuarios confían más en resultados orgánicos.\n"
            "• Ventaja competitiva duradera frente a competidores que solo dependen de pauta.\n"
            "• Mejora integral de la experiencia de usuario y velocidad del sitio.\n"
            "• Datos valiosos sobre comportamiento e intención de tu audiencia.\n\n"

            "QUÉ INCLUYE NUESTRO SERVICIO:\n\n"

            "• Auditoría SEO técnica completa (indexación, rastreo, errores, velocidad).\n"
            "• Análisis de Core Web Vitals y plan de optimización de rendimiento.\n"
            "• Investigación de palabras clave con análisis de volumen, dificultad e intención.\n"
            "• Análisis de brecha de contenido vs. competidores (content gap analysis).\n"
            "• Estrategia de clusters temáticos y arquitectura de contenidos.\n"
            "• Optimización on-page: títulos, meta descripciones, headings, URLs, imágenes.\n"
            "• Implementación de datos estructurados (JSON-LD): FAQ, HowTo, Product, Article, "
            "BreadcrumbList, Organization, LocalBusiness.\n"
            "• Optimización de interlinking y estructura de navegación.\n"
            "• Configuración y limpieza de sitemap XML, robots.txt y canonical tags.\n"
            "• Corrección de errores de rastreo (3xx, 4xx, 5xx) y cadenas de redirección.\n"
            "• Estrategia de link building ético (digital PR, guest posting, menciones).\n"
            "• Optimización para búsqueda local (Google Business Profile, NAP, reseñas).\n"
            "• Plan editorial mensual con contenidos optimizados para SEO.\n"
            "• Monitoreo de posiciones, tráfico orgánico y conversiones.\n"
            "• Reportes mensuales detallados con evolución y próximos pasos.\n\n"

            "PROCESO DE TRABAJO:\n\n"

            "1. Auditoría inicial: Rastreamos tu sitio completo con herramientas profesionales "
            "(Screaming Frog, Ahrefs, Search Console) para identificar todos los problemas "
            "técnicos, de contenido y de autoridad.\n"
            "2. Estrategia: Definimos las keywords objetivo, clusters temáticos, prioridades "
            "de optimización y calendario de contenidos.\n"
            "3. Optimización técnica: Corregimos errores de rastreo, mejoramos velocidad, "
            "implementamos datos estructurados y optimizamos la arquitectura del sitio.\n"
            "4. Contenido: Creamos y optimizamos contenidos alineados con la intención de "
            "búsqueda de tu audiencia objetivo.\n"
            "5. Autoridad: Ejecutamos estrategias de link building y digital PR para "
            "incrementar la autoridad de dominio.\n"
            "6. Monitoreo y ajuste: Seguimiento continuo de posiciones, tráfico y conversiones "
            "con ajustes mensuales basados en datos.\n\n"

            "HERRAMIENTAS QUE UTILIZAMOS:\n\n"

            "• Rastreo: Screaming Frog, Sitebulb, Google Search Console.\n"
            "• Keywords: Ahrefs, SEMrush, Google Keyword Planner, Answer The Public.\n"
            "• Rendimiento: Google PageSpeed Insights, GTmetrix, WebPageTest.\n"
            "• Analítica: Google Analytics 4, Looker Studio.\n"
            "• Monitoreo: Ahrefs Rank Tracker, Search Console Insights.\n"
            "• Contenido: Surfer SEO, Clearscope para optimización semántica.\n\n"

            "ENFOQUE E-E-A-T:\n\n"

            "Aplicamos las directrices de Google sobre Experiencia, Expertise, Autoridad y "
            "Confiabilidad (E-E-A-T) en cada aspecto de la estrategia: contenidos creados por "
            "expertos, fuentes citadas, perfiles de autor verificables, y señales de confianza "
            "como reseñas, certificaciones y menciones en medios.\n\n"

            "Palabras clave: posicionamiento web Colombia, agencia SEO, optimización para "
            "buscadores, SEO técnico, posicionamiento en Google, consultoría SEO, "
            "auditoría SEO, estrategia de contenidos SEO, link building Colombia."
        ),

        'Diseño Gráfico / Branding': (
            "Construye una marca memorable que conecte emocionalmente con tu audiencia y "
            "te diferencie en el mercado. Nuestro servicio de Diseño Gráfico y Branding va "
            "más allá de crear un logo bonito: desarrollamos sistemas de identidad visual "
            "completos que comunican los valores de tu empresa y generan confianza en cada "
            "punto de contacto con tus clientes.\n\n"

            "¿POR QUÉ ES CRUCIAL EL BRANDING PROFESIONAL?\n\n"

            "El 94% de las primeras impresiones están relacionadas con el diseño. Una identidad "
            "visual coherente aumenta el reconocimiento de marca hasta un 80% y los consumidores "
            "están dispuestos a pagar hasta un 20% más por marcas en las que confían. Tu marca "
            "es el activo más valioso de tu empresa: invertir en branding profesional es invertir "
            "en el crecimiento sostenible de tu negocio.\n\n"

            "BENEFICIOS PARA TU NEGOCIO:\n\n"

            "• Diferenciación clara frente a la competencia en mercados saturados.\n"
            "• Mayor recordación de marca (brand recall) en tu audiencia objetivo.\n"
            "• Coherencia visual en todos los canales: web, redes sociales, impresos y packaging.\n"
            "• Percepción de profesionalismo y confiabilidad que justifica precios premium.\n"
            "• Conexión emocional con tu público que genera lealtad a largo plazo.\n"
            "• Materiales listos para usar en cualquier medio y formato.\n"
            "• Guías claras para que tu equipo mantenga la consistencia de marca.\n\n"

            "QUÉ INCLUYE NUESTRO SERVICIO:\n\n"

            "• Sesión de descubrimiento de marca (brand discovery): valores, personalidad, "
            "audiencia, competencia y posicionamiento deseado.\n"
            "• Investigación de mercado y análisis de tendencias visuales del sector.\n"
            "• Diseño de logotipo principal con variaciones (horizontal, vertical, isotipo, imagotipo).\n"
            "• Paleta de colores primaria y secundaria con códigos HEX, RGB, CMYK y Pantone.\n"
            "• Selección tipográfica (fuentes principales y secundarias) con licencias incluidas.\n"
            "• Elementos gráficos complementarios: patrones, iconografía, texturas.\n"
            "• Manual de identidad de marca (Brand Book) de 20-40 páginas con:\n"
            "  - Filosofía y valores de marca.\n"
            "  - Uso correcto e incorrecto del logotipo.\n"
            "  - Espacios de protección y tamaños mínimos.\n"
            "  - Aplicaciones en fondos claros, oscuros y fotografías.\n"
            "  - Tono de voz y guía de comunicación.\n"
            "• Diseño de papelería corporativa: tarjetas de presentación, hoja membretada, "
            "sobre, carpeta, firma de correo electrónico.\n"
            "• Diseño de plantillas para redes sociales (posts, stories, covers).\n"
            "• Diseño de presentación corporativa (PowerPoint/Google Slides).\n"
            "• Archivos entregados en todos los formatos: AI, EPS, SVG, PDF, PNG, JPG, WebP.\n\n"

            "PROCESO DE TRABAJO:\n\n"

            "1. Inmersión: Entendemos tu negocio, valores, público objetivo y aspiraciones "
            "de marca a través de talleres y cuestionarios estratégicos.\n"
            "2. Investigación: Analizamos tu competencia, tendencias del sector y referencias "
            "visuales para definir la dirección creativa.\n"
            "3. Conceptualización: Desarrollamos 3 conceptos de marca diferenciados con "
            "moodboards, bocetos y justificación estratégica.\n"
            "4. Diseño: Refinamos el concepto elegido hasta lograr la versión final del "
            "logotipo y sistema visual completo.\n"
            "5. Aplicaciones: Diseñamos todas las piezas de papelería, redes sociales y "
            "materiales corporativos.\n"
            "6. Entrega: Compilamos el Brand Book, entregamos todos los archivos organizados "
            "y realizamos una sesión de capacitación sobre uso de marca.\n\n"

            "HERRAMIENTAS Y FORMATOS:\n\n"

            "• Diseño: Adobe Illustrator, Photoshop, InDesign, Figma.\n"
            "• Prototipado: Figma para mockups interactivos de aplicaciones de marca.\n"
            "• Formatos vectoriales: AI, EPS, SVG para escalabilidad infinita.\n"
            "• Formatos web: WebP, SVG optimizado, PNG con transparencia.\n"
            "• Formatos imprenta: PDF/X-4, CMYK con sangrado y marcas de corte.\n\n"

            "OPTIMIZACIÓN DIGITAL:\n\n"

            "Todos los activos digitales se entregan optimizados para web: imágenes comprimidas "
            "sin pérdida de calidad, SVGs minificados, nombres de archivo descriptivos para SEO, "
            "textos alternativos (alt text) recomendados, y formatos modernos (WebP/AVIF) para "
            "máxima velocidad de carga. Garantizamos accesibilidad AA en contraste de colores.\n\n"

            "Palabras clave: diseño de marca Colombia, branding corporativo, diseño de logotipo "
            "profesional, identidad visual, manual de marca, diseño gráfico empresarial, "
            "agencia de branding, imagen corporativa Colombia."
        ),

        'Automatización de Procesos': (
            "Elimina tareas repetitivas, reduce errores humanos y escala tu operación con "
            "nuestro servicio de Automatización de Procesos. Diseñamos e implementamos flujos "
            "de trabajo inteligentes que conectan tus herramientas, sistemas y equipos para "
            "que tu negocio funcione con máxima eficiencia mientras tu equipo se enfoca en "
            "lo que realmente importa: hacer crecer la empresa.\n\n"

            "¿POR QUÉ AUTOMATIZAR TUS PROCESOS?\n\n"

            "Las empresas que automatizan sus procesos reportan una reducción del 30-50% en "
            "costos operativos y un aumento del 20% en productividad. Cada tarea manual "
            "repetitiva es una oportunidad de automatización: desde la captura de leads hasta "
            "la facturación, desde la gestión de inventarios hasta el servicio al cliente. "
            "La automatización no reemplaza a tu equipo, lo potencia.\n\n"

            "BENEFICIOS PARA TU NEGOCIO:\n\n"

            "• Reducción de hasta un 50% en tiempo dedicado a tareas operativas repetitivas.\n"
            "• Eliminación de errores humanos en procesos críticos como facturación y reportes.\n"
            "• Respuesta instantánea a clientes con chatbots y flujos automatizados.\n"
            "• Escalabilidad: procesos que funcionan igual con 10 o 10,000 operaciones diarias.\n"
            "• Visibilidad total del estado de cada proceso con dashboards en tiempo real.\n"
            "• Integración de todas tus herramientas en un ecosistema conectado.\n"
            "• ROI demostrable desde el primer trimestre de implementación.\n\n"

            "QUÉ INCLUYE NUESTRO SERVICIO:\n\n"

            "• Mapeo y diagnóstico de procesos actuales (AS-IS) con identificación de cuellos "
            "de botella y oportunidades de automatización.\n"
            "• Diseño de procesos optimizados (TO-BE) con diagramas BPMN.\n"
            "• Desarrollo de integraciones API entre sistemas (CRM, ERP, e-commerce, contabilidad).\n"
            "• Configuración de flujos en plataformas no-code/low-code (Zapier, Make/Integromat, "
            "Power Automate, n8n).\n"
            "• Desarrollo de automatizaciones personalizadas con Python, Celery y Django.\n"
            "• Implementación de chatbots inteligentes para atención al cliente.\n"
            "• Automatización de email marketing: secuencias de bienvenida, nurturing, "
            "recuperación de carritos y seguimiento post-venta.\n"
            "• Automatización de facturación, cobros y recordatorios de pago.\n"
            "• Generación automática de reportes y dashboards.\n"
            "• Notificaciones inteligentes por email, SMS y WhatsApp Business API.\n"
            "• Webhooks y event-driven architecture para procesos en tiempo real.\n"
            "• Documentación completa de cada automatización implementada.\n\n"

            "PROCESO DE TRABAJO:\n\n"

            "1. Diagnóstico: Mapeamos todos tus procesos actuales, identificamos tareas "
            "repetitivas, puntos de fricción y oportunidades de mejora.\n"
            "2. Priorización: Clasificamos las automatizaciones por impacto vs. esfuerzo "
            "para implementar primero las de mayor ROI.\n"
            "3. Diseño: Creamos los flujos automatizados con diagramas claros, definimos "
            "triggers, condiciones y acciones.\n"
            "4. Desarrollo: Implementamos las integraciones y automatizaciones con pruebas "
            "exhaustivas en ambiente de staging.\n"
            "5. Despliegue: Activamos en producción con monitoreo intensivo durante las "
            "primeras semanas.\n"
            "6. Optimización: Ajustamos basándonos en métricas reales y expandimos a "
            "nuevos procesos según resultados.\n\n"

            "STACK TECNOLÓGICO:\n\n"

            "• Orquestación: Zapier, Make (Integromat), n8n, Power Automate.\n"
            "• Desarrollo: Python, Django, Celery, Redis, RabbitMQ.\n"
            "• APIs: REST, GraphQL, webhooks, OAuth2, API Keys.\n"
            "• Bases de datos: PostgreSQL, MongoDB para datos no estructurados.\n"
            "• Mensajería: WhatsApp Business API, Twilio, SendGrid.\n"
            "• CRM/ERP: HubSpot, Salesforce, Odoo, Siigo.\n"
            "• Monitoreo: Sentry, logs estructurados, alertas automáticas.\n"
            "• Infraestructura: Docker, colas de mensajes, reintentos idempotentes.\n\n"

            "CASOS DE USO COMUNES:\n\n"

            "• Lead capturado en formulario web → se crea contacto en CRM → se envía email "
            "de bienvenida → se asigna a vendedor → se programa seguimiento automático.\n"
            "• Pedido confirmado en e-commerce → se genera factura → se notifica al almacén "
            "→ se envía tracking al cliente → se programa encuesta de satisfacción.\n"
            "• Ticket de soporte creado → se clasifica por IA → se asigna al agente correcto "
            "→ se escala automáticamente si no hay respuesta en X horas.\n\n"

            "Palabras clave: automatización de procesos Colombia, integración de sistemas, "
            "automatización empresarial, RPA Colombia, flujos de trabajo automatizados, "
            "integración API, chatbots empresariales, transformación digital."
        ),

        'Consultoría Digital': (
            "Toma las decisiones tecnológicas correctas con nuestro servicio de Consultoría "
            "Digital. Ofrecemos acompañamiento estratégico experto para empresas que quieren "
            "transformarse digitalmente de forma inteligente, con un roadmap claro, prioridades "
            "definidas por impacto y un plan de ejecución realista que alinea tecnología con "
            "objetivos de negocio.\n\n"

            "¿POR QUÉ NECESITAS CONSULTORÍA DIGITAL?\n\n"

            "El 70% de los proyectos de transformación digital fracasan por falta de estrategia, "
            "no por falta de tecnología. Antes de invertir en herramientas, plataformas o "
            "desarrollos, necesitas un diagnóstico honesto de tu situación actual y un plan "
            "que priorice las iniciativas con mayor retorno. Nuestros consultores tienen "
            "experiencia real implementando soluciones digitales para empresas de todos los "
            "tamaños en Latinoamérica.\n\n"

            "BENEFICIOS PARA TU NEGOCIO:\n\n"

            "• Claridad estratégica: sabrás exactamente qué hacer, en qué orden y por qué.\n"
            "• Reducción de riesgo: evita inversiones en tecnología que no necesitas.\n"
            "• Alineación organizacional: todos los stakeholders con la misma visión.\n"
            "• Priorización por ROI: enfócate en las iniciativas que generan mayor impacto.\n"
            "• Independencia tecnológica: te ayudamos a elegir sin atarte a un proveedor.\n"
            "• Aceleración del time-to-market de tus iniciativas digitales.\n"
            "• Gobernanza tecnológica que previene deuda técnica y caos operativo.\n\n"

            "QUÉ INCLUYE NUESTRO SERVICIO:\n\n"

            "• Diagnóstico de madurez digital: evaluamos tu situación actual en 8 dimensiones "
            "(estrategia, tecnología, datos, procesos, personas, cultura, cliente, innovación).\n"
            "• Análisis de ecosistema tecnológico actual: herramientas, integraciones, "
            "deuda técnica y oportunidades de consolidación.\n"
            "• Benchmarking competitivo y análisis de mejores prácticas del sector.\n"
            "• Talleres de co-creación con stakeholders para definir visión y prioridades.\n"
            "• Roadmap de transformación digital a 6-12-18 meses con hitos claros.\n"
            "• Matriz de priorización impacto/esfuerzo de todas las iniciativas.\n"
            "• Arquitectura de referencia tecnológica recomendada.\n"
            "• Plan de datos: qué medir, cómo medir y qué decisiones tomar con los datos.\n"
            "• Definición de KPIs y OKRs para cada iniciativa.\n"
            "• Backlog priorizado listo para ejecución.\n"
            "• Evaluación y selección de proveedores tecnológicos.\n"
            "• Plan de gestión del cambio y adopción tecnológica.\n"
            "• Acompañamiento en la ejecución de las primeras iniciativas.\n\n"

            "PROCESO DE TRABAJO:\n\n"

            "1. Inmersión: Entrevistas con líderes de negocio y tecnología, revisión de "
            "sistemas actuales, análisis de datos y métricas existentes.\n"
            "2. Diagnóstico: Evaluación de madurez digital, identificación de brechas "
            "y oportunidades, análisis FODA tecnológico.\n"
            "3. Estrategia: Definición de visión digital, priorización de iniciativas "
            "y diseño del roadmap con quick wins y proyectos estructurales.\n"
            "4. Arquitectura: Diseño de la arquitectura tecnológica objetivo, selección "
            "de herramientas y definición de estándares.\n"
            "5. Plan de ejecución: Backlog detallado, estimaciones, dependencias, "
            "recursos necesarios y cronograma.\n"
            "6. Acompañamiento: Seguimiento quincenal de la ejecución, resolución de "
            "bloqueos y ajuste de prioridades según resultados.\n\n"

            "ÁREAS DE ESPECIALIZACIÓN:\n\n"

            "• Transformación digital para PYMEs y empresas en crecimiento.\n"
            "• Estrategia de e-commerce y marketplaces.\n"
            "• Arquitectura de datos y business intelligence.\n"
            "• Selección e implementación de CRM/ERP.\n"
            "• Estrategia de contenidos y SEO corporativo.\n"
            "• Optimización de experiencia de cliente (CX) digital.\n"
            "• Migración a la nube y modernización de sistemas legacy.\n"
            "• Estrategia de ciberseguridad y cumplimiento normativo.\n\n"

            "ENTREGABLES:\n\n"

            "• Documento de diagnóstico de madurez digital (30-50 páginas).\n"
            "• Roadmap visual de transformación digital.\n"
            "• Matriz de priorización de iniciativas.\n"
            "• Arquitectura de referencia tecnológica.\n"
            "• Backlog priorizado con user stories.\n"
            "• Plan de KPIs y OKRs.\n"
            "• Presentación ejecutiva para directivos.\n"
            "• Sesiones de transferencia de conocimiento al equipo interno.\n\n"

            "Palabras clave: consultoría digital Colombia, transformación digital empresas, "
            "estrategia digital, consultoría tecnológica, roadmap digital, asesoría en "
            "tecnología, consultoría TI Colombia, transformación digital PYMEs."
        ),
    }

    for name, desc in descriptions.items():
        try:
            svc = Service.objects.filter(name=name).first()
            if svc:
                svc.description = desc
                svc.save(update_fields=['description'])
        except Exception:
            pass


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_fill_all_service_descriptions'),
    ]

    operations = [
        migrations.RunPython(update_complete_descriptions, noop),
    ]
