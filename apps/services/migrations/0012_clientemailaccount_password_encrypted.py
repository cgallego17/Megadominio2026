# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_cpanel_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientemailaccount',
            name='password_encrypted',
            field=models.CharField(
                blank=True,
                help_text='Se guarda cifrada para poder mostrarla en el dashboard.',
                max_length=500,
                verbose_name='Contraseña (cifrada)',
            ),
        ),
    ]
