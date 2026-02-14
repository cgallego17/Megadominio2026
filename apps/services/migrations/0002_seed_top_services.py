from django.db import migrations
from decimal import Decimal


def seed_top_services(apps, schema_editor):
    Service = apps.get_model('services', 'Service')

    seed = [
        dict(
            name="Desarrollo Web",
            description=(
                "Sitios web corporativos, landing pages y e‑commerce modernos que "
                "convierten visitantes en clientes."
            ),
            price=Decimal('2500000'),
            billing_type='unique',
            is_active=True,
        ),
        dict(
            name="Marketing Digital",
            description=(
                "Gestión profesional de campañas en Google Ads y Meta Ads con ROI medible "
                "para impulsar tus ventas."
            ),
            price=Decimal('1500000'),
            billing_type='monthly',
            is_active=True,
        ),
        dict(
            name="SEO / Posicionamiento",
            description=(
                "Optimización para motores de búsqueda que genera tráfico orgánico de calidad "
                "y visibilidad sostenible."
            ),
            price=Decimal('1800000'),
            billing_type='monthly',
            is_active=True,
        ),
        dict(
            name="Diseño Gráfico / Branding",
            description=(
                "Identidad visual, logos y materiales que diferencian tu marca en mercados competitivos."
            ),
            price=Decimal('1200000'),
            billing_type='unique',
            is_active=True,
        ),
        dict(
            name="Automatización de Procesos",
            description=(
                "Integraciones, APIs y automatización con Zapier, CRM y RPA para máxima eficiencia operativa."
            ),
            price=Decimal('2000000'),
            billing_type='unique',
            is_active=True,
        ),
        dict(
            name="Consultoría Digital",
            description=(
                "Estrategia digital integral, auditorías y roadmaps personalizados para transformación empresarial."
            ),
            price=Decimal('900000'),
            billing_type='unique',
            is_active=True,
        ),
    ]

    for data in seed:
        Service.objects.update_or_create(
            name=data['name'],
            defaults=data,
        )


def unseed_top_services(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    names = [
        "Desarrollo Web",
        "Marketing Digital",
        "SEO / Posicionamiento",
        "Diseño Gráfico / Branding",
        "Automatización de Procesos",
        "Consultoría Digital",
    ]
    Service.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_top_services, unseed_top_services),
    ]
