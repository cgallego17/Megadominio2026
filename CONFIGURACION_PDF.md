# Configuración del PDF de Cuentas de Cobro

Este documento explica cómo personalizar el formato y contenido de los PDFs de cuentas de cobro.

## 📍 Ubicación de la configuración

Archivo: `megadominio/settings.py`

## 🔧 Parámetros configurables

### Información del Emisor

```python
CUENTA_COBRO_EMISOR_NOMBRE = 'CRISTIAN GALLEGO ARBOLEDA'
CUENTA_COBRO_EMISOR_DOCUMENTO = 'C.C. 1.036.640.871'
CUENTA_COBRO_EMISOR_DIRECCION = 'Cr 58F #63A-21'
CUENTA_COBRO_EMISOR_CIUDAD = 'Medellín, Antioquia'
CUENTA_COBRO_EMISOR_TELEFONO = '300 860 1310'
CUENTA_COBRO_EMISOR_EMAIL = 'info@megadominio.co'
```

### Mensajes de Garantía (se seleccionan automáticamente)

#### Para Productos Físicos (Hardware/Componentes)
```python
CUENTA_COBRO_OBS_PRODUCTOS = 'Garantía de montaje 30 días sobre mano de obra. Los componentes tienen garantía del fabricante según cada pieza. La garantía no cubre daños por mal uso, manipulación inadecuada o factores externos.'
```

**Se usa cuando la cuenta incluye:**
- Procesadores, CPUs (Intel, Ryzen)
- Tarjetas madre (ASUS, Prime, etc.)
- Memorias RAM (DDR4, DDR5)
- Discos (SSD, HDD, NVMe, M.2)
- Fuentes de poder (PSU, Bronze, Gold)
- Tarjetas gráficas (GPU, NVIDIA, AMD)
- Monitores, teclados, mouse
- Cualquier componente físico de computador

#### Para Servicios Digitales
```python
CUENTA_COBRO_OBS_SERVICIOS = 'Garantía de 30 días sobre el servicio prestado. Soporte técnico y actualizaciones incluidas durante el período de garantía. Renovación automática según términos acordados.'
```

**Se usa cuando la cuenta incluye:**
- Hosting, dominios, servidores
- Desarrollo web, diseño
- Mantenimiento, soporte
- Email, SSL, certificados
- SEO, marketing digital
- Licencias, suscripciones
- Servicios mensuales o anuales

#### Para Cuentas Mixtas (Productos + Servicios)
```python
CUENTA_COBRO_OBS_MIXTO = 'Garantía de 30 días sobre mano de obra y servicios prestados. Los componentes físicos tienen garantía del fabricante según cada pieza. Soporte técnico incluido.'
```

**Se usa cuando la cuenta incluye ambos tipos.**

### Texto Legal
```python
CUENTA_COBRO_TEXTO_LEGAL = 'Conforme al parágrafo 2 del art 383 ET, informo que no he sido contratado o vinculado las (2) o más trabajadores asociados a mi actividad. NO PRACTICAR RETENCION EN LA FUENTE.'
```

## 🎨 Logo de la Empresa

El sistema busca automáticamente el logo en estas ubicaciones (en orden):

1. `static/img/logo.png`
2. `static/img/logo.jpg`
3. `static/images/logo.png`
4. `staticfiles/img/logo.png`

**Recomendaciones para el logo:**
- Formato: PNG (con fondo transparente) o JPG
- Dimensiones: Ancho máximo 400px, Alto máximo 150px
- El sistema lo redimensionará automáticamente a 1.2" × 0.4"

Si no encuentra el logo, mostrará "MEGADOMINIO" en texto.

## 🤖 Detección Automática

El sistema analiza cada item de la cuenta de cobro para determinar si es producto físico o servicio:

### Palabras clave para Productos Físicos:
- procesador, cpu, ryzen, intel, core
- tarjeta, madre, motherboard, asus, prime
- memoria, ram, ddr, ddr4, ddr5
- disco, ssd, hdd, nvme, m.2, sata
- fuente, poder, psu, power, watts
- gpu, gráfica, nvidia, amd, radeon, geforce
- monitor, teclado, mouse
- componente, hardware, montaje, ensamblaje

### Palabras clave para Servicios:
- hosting, dominio, servidor, vps
- desarrollo, diseño, web, sitio
- mantenimiento, soporte, actualización
- email, correo, ssl, certificado
- seo, marketing, optimización
- licencia, suscripción, plan
- mensual, anual, recurrente

### Tipo de Facturación:
- `unique` (Pago único) → Generalmente productos físicos
- `monthly` (Mensual) → Servicios recurrentes
- `annual` (Anual) → Servicios recurrentes

## 📝 Notas Personalizadas

Si agregas notas en el campo `notes` de una cuenta de cobro, ese texto tendrá prioridad sobre la detección automática.

## 🔄 Formato de Números

- Separador de miles: Punto (`.`)
- Sin decimales
- Ejemplo: `$3.800.000`

## 📄 Estructura del PDF

1. **Header**
   - Logo (izquierda)
   - "CUENTA DE COBRO #XXX" (centro)
   - Fecha (derecha)

2. **Información en dos columnas**
   - Emisor (izquierda)
   - Cliente (derecha)

3. **Tabla de Items**
   - Fondo negro en encabezado
   - Columnas: Descripción, Cantidad, Valor Unitario, Subtotal

4. **Total**
   - Formato destacado: "TOTAL A PAGAR: $X.XXX.XXX"

5. **Observaciones**
   - Mensaje de garantía (automático o personalizado)

6. **Firma**
   - Línea de firma
   - Nombre y documento del emisor

7. **Texto Legal**
   - Información sobre retención en la fuente

## 🚀 Uso

1. Ve a `/dashboard/cuentas-cobro/`
2. Selecciona una cuenta de cobro
3. Haz clic en "Descargar PDF"

El sistema generará automáticamente el PDF con el formato profesional.

## ⚙️ Personalización Avanzada

Si necesitas modificar la detección automática, edita el archivo:
`apps/core/dashboard_views.py` → función `dashboard_cuenta_pdf`

Busca las listas `keywords_productos` y `keywords_servicios` para agregar más palabras clave.

## 📞 Soporte

Para cualquier duda o personalización adicional, contacta con el desarrollador.
