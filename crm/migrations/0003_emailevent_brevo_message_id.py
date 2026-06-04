# Generated manually — EmailEvent model + brevo_message_id in SentEmail

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_tag_contacttag_broadcast'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='sentemail',
            name='brevo_message_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Brevo Message ID'),
        ),
        migrations.CreateModel(
            name='EmailEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=30, verbose_name='Tipo de evento')),
                ('email', models.EmailField(max_length=254, verbose_name='Email del destinatario')),
                ('message_id', models.CharField(blank=True, max_length=100, verbose_name='Message ID')),
                ('link', models.URLField(blank=True, verbose_name='Link clickeado')),
                ('extra_data', models.JSONField(blank=True, default=dict, verbose_name='Datos extra')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_email', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='crm.sentemail')),
                ('subscriber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_events', to='crm.subscriber')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Evento de email',
                'verbose_name_plural': 'Eventos de email',
                'indexes': [
                    models.Index(fields=['subscriber', 'event_type']),
                    models.Index(fields=['message_id']),
                ],
            },
        ),
    ]
