# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0012_clientemailaccount_password_encrypted'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('smtp_host', models.CharField(blank=True, help_text='Ej: mail.tudominio.com o smtp.gmail.com', max_length=255, verbose_name='Host SMTP')),
                ('smtp_port', models.PositiveIntegerField(default=465, verbose_name='Puerto SMTP')),
                ('smtp_use_ssl', models.BooleanField(default=True, verbose_name='Usar SSL')),
                ('smtp_use_tls', models.BooleanField(default=False, verbose_name='Usar TLS')),
                ('smtp_user', models.CharField(blank=True, max_length=255, verbose_name='Usuario SMTP')),
                ('smtp_password_encrypted', models.CharField(blank=True, max_length=500, verbose_name='Contraseña SMTP (cifrada)')),
                ('default_from_email', models.CharField(blank=True, help_text='Ej: Megadominio <soporte@tudominio.com>', max_length=255, verbose_name='Remitente por defecto')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Actualizado')),
            ],
            options={
                'verbose_name': 'Configuración SMTP',
                'verbose_name_plural': 'Configuración SMTP',
            },
        ),
    ]
