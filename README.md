# Megadominio - Plataforma de Servicios Digitales

Megadominio es una plataforma web profesional para la venta, gestión y facturación de servicios digitales, construida con Django y enfocada en proporcionar una experiencia moderna y escalable.

## 🚀 Características Principales

### 🏠 Home Comercial
- **Hero impactante** con mensaje claro de valor y llamados a la acción
- **Sección de servicios** con tarjetas visuales y precios dinámicos
- **Beneficios destacados** (seguridad, soporte, escalabilidad, experiencia)
- **Flujo de trabajo** visual y claro
- **Testimonios de clientes** para generar confianza
- **Diseño 100% responsive** y mobile-first

### 📊 Dashboard Administrativo
- **Métricas en tiempo real**: cotizaciones, clientes, servicios, ingresos
- **Gráficos interactivos** de estado de cotizaciones y facturas
- **Actividad reciente** con acceso rápido a funciones principales
- **Servicios más solicitados** para análisis de negocio
- **Interfaz intuitiva** con navegación lateral optimizada

### 💼 Gestión de Cotizaciones
- **Creación dinámica** de cotizaciones con múltiples servicios
- **Estados configurables**: borrador, enviada, aceptada, rechazada, expirada
- **Cálculo automático** de subtotales, descuentos e impuestos
- **Exportación a PDF** y envío por correo electrónico
- **Validación de fechas** y control de vigencia

### 🧾 Sistema de Facturación
- **Generación automática** desde cotizaciones aceptadas
- **Numeración automática** y consecutiva
- **Control de estados**: pendiente, pagada, vencida, cancelada
- **Cálculo de impuestos** y totales automáticos
- **Historial de pagos** y fechas de vencimiento

### 👥 Gestión de Clientes
- **Perfil completo** con información de contacto y documentos
- **Historial de cotizaciones** y servicios activos
- **Estado de cuentas** y facturas pendientes
- **Segmentación** por tipo y actividad

### 🛠️ Gestión de Servicios
- **Catálogo configurable** de servicios
- **Tipos de facturación**: único, mensual, anual
- **Asignación a clientes** con seguimiento de estado
- **Precios dinámicos** y descripciones detalladas

### 🔐 Sistema de Usuarios y Roles
- **Modelo de usuario personalizado** con roles definidos
- **Permisos granulares**: administrador, asesor, vendedor, cliente
- **Autenticación segura** con Django
- **Perfiles extendidos** con preferencias y configuraciones

## 🛠️ Stack Tecnológico

### Backend
- **Django 4.2.7** - Framework principal
- **Django REST Framework** - API REST
- **PostgreSQL** - Base de datos (configurable a SQLite para desarrollo)
- **Python 3.14** - Lenguaje de programación

### Frontend
- **Bootstrap 5.3.0** - Framework CSS
- **Font Awesome 6.0** - Iconos
- **JavaScript Vanilla** - Interactividad
- **Templates Django** - Renderizado del lado del servidor

### Herramientas Adicionales
- **ReportLab** - Generación de PDFs
- **Django Crispy Forms** - Formularios optimizados
- **WhiteNoise** - Manejo de archivos estáticos
- **Celery** (configurado) - Tareas asíncronas

## 📁 Estructura del Proyecto

```
megadominio/
├── apps/
│   ├── accounts/          # Gestión de usuarios y autenticación
│   ├── clients/           # Gestión de clientes
│   ├── services/         # Catálogo de servicios
│   ├── quotes/            # Sistema de cotizaciones
│   ├── invoices/          # Sistema de facturación
│   └── core/              # Vistas principales y utilidades
├── templates/             # Templates HTML
├── static/               # Archivos estáticos (CSS, JS, imágenes)
├── media/                # Archivos multimedia subidos
├── megadominio/           # Configuración principal de Django
├── requirements.txt       # Dependencias Python
├── .env                  # Variables de entorno
└── manage.py            # Script de gestión Django
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.14+
- PostgreSQL (opcional, usa SQLite por defecto)
- pip y virtualenv

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd megadominio
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Migrar base de datos
```bash
python manage.py migrate
```

### 6. Crear superusuario
```bash
python manage.py createsuperuser
```

### 7. Ejecutar servidor de desarrollo
```bash
python manage.py runserver
```

## 📊 Modelos de Datos

### Usuarios (accounts.User)
- **Roles**: admin, advisor, seller, client
- **Campos extendidos**: teléfono, avatar, verificación
- **Perfil relacionado**: preferencias y configuraciones

### Clientes (clients.Client)
- **Información básica**: nombre, email, teléfono
- **Documentos**: tipo y número de identificación
- **Empresa**: nombre y dirección corporativa

### Servicios (services.Service)
- **Información**: nombre, descripción, precio
- **Facturación**: único, mensual, anual
- **Estado**: activo/inactivo

### Cotizaciones (quotes.Quote)
- **Datos**: número, cliente, estado, fechas
- **Financieros**: subtotales, descuentos, impuestos, total
- **Items**: servicios asociados con cantidades y precios

### Facturas (invoices.Invoice)
- **Generación**: automática desde cotización aceptada
- **Control**: numeración, fechas, estados de pago
- **Items**: replicados desde la cotización original

## 🔧 Configuración Adicional

### Base de Datos PostgreSQL
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'megadominio',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Configuración de Email
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 🚀 Despliegue

### Producción
1. **Variables de entorno**: Configurar `DEBUG=False`
2. **Base de datos**: Usar PostgreSQL
3. **Archivos estáticos**: `python manage.py collectstatic`
4. **Servidor web**: Gunicorn + Nginx
5. **SSL**: Configurar certificado HTTPS

### Docker (Opcional)
```dockerfile
# Dockerfile
FROM python:3.14
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "megadominio.wsgi:application"]
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Pull Request

## 📝 Licencia

Este proyecto está licenciado bajo la MIT License.

## 🆘 Soporte

Para soporte técnico:
- **Email**: info@megadominio.com
- **Teléfono**: +504 1234-5678
- **Documentación**: [Wiki del proyecto]

## 🔄 Roadmap

### Versión 1.1 (Próxima)
- [ ] Pasarela de pagos integrada
- [ ] Sistema de suscripciones automáticas
- [ ] Notificaciones por SMS
- [ ] API REST completa

### Versión 1.2 (Futura)
- [ ] Módulo CRM avanzado
- [ ] Automatización de correos
- [ ] Reportes y analytics
- [ ] Aplicación móvil

---

**Desarrollado con ❤️ por el equipo de Megadominio**
