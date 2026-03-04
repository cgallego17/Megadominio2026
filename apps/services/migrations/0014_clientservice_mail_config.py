# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_add_email_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientservice',
            name='mail_imap_host',
            field=models.CharField(blank=True, help_text='Ej: mail.tudominio.com. El cliente verá esta configuración.', max_length=255, verbose_name='Servidor IMAP'),
        ),
        migrations.AddField(
            model_name='clientservice',
            name='mail_imap_port',
            field=models.PositiveIntegerField(default=993, verbose_name='Puerto IMAP'),
        ),
        migrations.AddField(
            model_name='clientservice',
            name='mail_imap_ssl',
            field=models.BooleanField(default=True, verbose_name='IMAP SSL'),
        ),
        migrations.AddField(
            model_name='clientservice',
            name='mail_smtp_host',
            field=models.CharField(blank=True, help_text='Ej: mail.tudominio.com', max_length=255, verbose_name='Servidor SMTP'),
        ),
        migrations.AddField(
            model_name='clientservice',
            name='mail_smtp_port',
            field=models.PositiveIntegerField(default=465, verbose_name='Puerto SMTP'),
        ),
        migrations.AddField(
            model_name='clientservice',
            name='mail_smtp_ssl',
            field=models.BooleanField(default=True, verbose_name='SMTP SSL'),
        ),
        migrations.AddField(
            model_name='clientservice',
            name='mail_config_notes',
            field=models.TextField(blank=True, help_text='Instrucciones adicionales que verá el cliente (ej: usar autenticación).', verbose_name='Notas de configuración'),
        ),
    ]
