from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    for svc in Service.objects.all():
        base = slugify(svc.name)
        slug = base
        n = 1
        while Service.objects.filter(
            slug=slug
        ).exclude(pk=svc.pk).exists():
            slug = f'{base}-{n}'
            n += 1
        svc.slug = slug
        svc.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_complete_all_descriptions'),
    ]

    operations = [
        # Step 1: Add slug field WITHOUT unique constraint
        migrations.AddField(
            model_name='service',
            name='slug',
            field=models.SlugField(
                blank=True, default='', max_length=250,
                verbose_name='Slug',
            ),
            preserve_default=False,
        ),
        # Step 2: Populate slugs for existing services
        migrations.RunPython(
            populate_slugs,
            migrations.RunPython.noop,
        ),
        # Step 3: Add unique constraint
        migrations.AlterField(
            model_name='service',
            name='slug',
            field=models.SlugField(
                blank=True, max_length=250, unique=True,
                verbose_name='Slug',
            ),
        ),
    ]
