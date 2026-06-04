"""
Migration: recrea EmailEvent con el esquema actual y corrige SentEmail.brevo_message_id
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_emailevent_brevo_message_id'),
    ]

    operations = [
        # Ampliar max_length de brevo_message_id (100 → 255)
        migrations.AlterField(
            model_name='sentemail',
            name='brevo_message_id',
            field=models.CharField(
                blank=True,
                max_length=255,
                help_text='Message-ID de Brevo para tracking de eventos',
            ),
        ),

        # Recrear EmailEvent con el esquema actual
        migrations.DeleteModel(name='EmailEvent'),
        migrations.CreateModel(
            name='EmailEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(
                    max_length=20,
                    choices=[
                        ('opened', 'Abierto'),
                        ('clicked', 'Click'),
                        ('bounced', 'Rebotado'),
                        ('unsubscribed', 'Desuscrito'),
                        ('delivered', 'Entregado'),
                        ('spam', 'Spam'),
                    ],
                )),
                ('metadata', models.JSONField(
                    default=dict,
                    blank=True,
                    help_text='Datos extra del evento (link clickeado, IP, etc.)',
                )),
                ('occurred_at', models.DateTimeField(
                    help_text='Cuándo ocurrió el evento según Brevo',
                )),
                ('fetched_at', models.DateTimeField(
                    auto_now_add=True,
                    help_text='Cuándo se trajo de la API',
                )),
                ('subscriber', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='email_events',
                    to='crm.subscriber',
                )),
                ('sent_email', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='events',
                    to='crm.sentemail',
                )),
            ],
            options={
                'verbose_name': 'Evento de email',
                'verbose_name_plural': 'Eventos de email',
                'ordering': ['-occurred_at'],
                'indexes': [
                    models.Index(fields=['subscriber', 'event_type'], name='emailevent_sub_evt_idx'),
                    models.Index(fields=['event_type', 'occurred_at'], name='emailevent_evt_occ_idx'),
                ],
            },
        ),
    ]
